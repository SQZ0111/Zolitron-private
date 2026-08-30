import io
from dataclasses import dataclass, field

from PIL import Image as PillowImage
from sqlalchemy.orm import Session

from app.repositories.image_processing import ImageProcessingRepository
from app.schemas.api import ClassificationRead
from app.services.catalog import CatalogService
from app.services.detection import CONFIDENCE_THRESHOLDS, DetectionService
from app.services.image_storage import LocalImageStorage

# MVP calibration values. Litter alone only earns a collection recommendation
# when it covers enough of the frame or is scattered over enough detections.
# Both numbers are provisional and should be re-tuned against labelled images.
LITTER_COLLECT_COVERAGE = 0.12
LITTER_COLLECT_COUNT = 6


class ImageValidationError(ValueError):
    pass


@dataclass
class ClassificationSummary:
    """Everything one image's accepted detections say about it."""

    label: str
    confidence: float
    status: str
    bbox: dict | None = None
    disposition: str | None = None
    garbage_coverage: float = 0.0
    litter_coverage: float = 0.0
    garbage_count: int = 0
    litter_count: int = 0
    detections: list[dict] = field(default_factory=list)


class ImageProcessingService:
    def __init__(
        self,
        db: Session,
        *,
        detector: DetectionService | None = None,
        storage: LocalImageStorage | None = None,
    ):
        self.db = db
        self.repository = ImageProcessingRepository(db)
        self.detector = detector
        self.storage = storage or LocalImageStorage()

    @staticmethod
    def validate_city(city: str) -> str:
        normalized_city = city.strip()
        if not normalized_city:
            raise ImageValidationError("City must not be empty.")
        return normalized_city

    @staticmethod
    def validate_image(content: bytes) -> str:
        try:
            with PillowImage.open(io.BytesIO(content)) as image:
                image.verify()
                image_format = image.format
        except Exception as exc:
            raise ImageValidationError(
                "The uploaded file is not a valid JPEG or PNG image."
            ) from exc

        extensions = {"JPEG": "jpg", "PNG": "png"}
        if image_format not in extensions:
            raise ImageValidationError("Only JPEG and PNG images are supported.")
        return extensions[image_format]

    @staticmethod
    def read_image_dimensions(content: bytes) -> tuple[int, int]:
        with PillowImage.open(io.BytesIO(content)) as image:
            return image.size

    def store_and_classify(
        self,
        *,
        content: bytes,
        city: str,
        country: str,
        latitude: float | None,
        longitude: float | None,
        source: str,
        namespace: str,
    ) -> ClassificationRead:
        city = self.validate_city(city)
        extension = self.validate_image(content)
        width, height = self.read_image_dimensions(content)
        stored = self.storage.save(content, extension, namespace)

        existing = self.repository.get_classification_by_storage_path(
            stored.storage_path
        )
        if existing:
            return CatalogService(self.db).classification_to_schema(existing)

        image = self.repository.get_image_by_storage_path(stored.storage_path)
        if image:
            image = self.repository.prepare_existing_image(
                image,
                source=source,
                img_url=stored.public_url,
                city=city,
                country=country,
                latitude=latitude,
                longitude=longitude,
                width=width,
                height=height,
            )
        else:
            image = self.repository.create_image(
                source=source,
                img_url=stored.public_url,
                storage_path=stored.storage_path,
                city=city,
                country=country,
                latitude=latitude,
                longitude=longitude,
                width=width,
                height=height,
            )
        self.db.commit()

        try:
            detector = self.detector or DetectionService()
            output = detector.detect_trash(stored.absolute_path)
            summary = self._summarize_output(output, width, height)
            classification = self.repository.create_classification(
                image=image,
                label_name=summary.label,
                confidence=summary.confidence,
                status=summary.status,
                model_version=detector.workflow_id,
                bbox=summary.bbox,
                disposition=summary.disposition,
                garbage_coverage=summary.garbage_coverage,
                litter_coverage=summary.litter_coverage,
                garbage_count=summary.garbage_count,
                litter_count=summary.litter_count,
                detections=summary.detections,
            )
        except Exception:
            self.repository.mark_failed(image)
            raise

        return CatalogService(self.db).classification_to_schema(classification)

    @staticmethod
    def _to_bbox(detection: dict) -> dict:
        return {
            "x": detection.get("x"),
            "y": detection.get("y"),
            "width": detection.get("width"),
            "height": detection.get("height"),
        }

    @staticmethod
    def _coverage(detections: list[dict], image_width: int, image_height: int) -> float:
        frame_area = float(image_width or 0) * float(image_height or 0)
        if frame_area <= 0:
            return 0.0

        covered = sum(
            float(detection.get("width") or 0) * float(detection.get("height") or 0)
            for detection in detections
        )
        return min(covered / frame_area, 1.0)

    @classmethod
    def _decide_disposition(
        cls,
        *,
        garbage_count: int,
        litter_count: int,
        litter_coverage: float,
    ) -> str:
        """Garbage always earns a collection; litter only escalates upward."""
        if garbage_count >= 1:
            return "collect"
        if litter_count >= 1:
            if (
                litter_coverage >= LITTER_COLLECT_COVERAGE
                or litter_count >= LITTER_COLLECT_COUNT
            ):
                return "collect"
            return "watch"
        return "not-garbage"

    @classmethod
    def _summarize_output(
        cls,
        output: dict,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> ClassificationSummary:
        detections = output.get("predictions", {}).get("predictions", [])
        supported = [
            detection
            for detection in detections
            if detection.get("class") in CONFIDENCE_THRESHOLDS
        ]
        accepted = [
            detection
            for detection in supported
            if float(detection.get("confidence", 0))
            >= CONFIDENCE_THRESHOLDS[detection["class"]]
        ]

        if accepted:
            garbage = [item for item in accepted if item.get("class") == "garbage"]
            litter = [item for item in accepted if item.get("class") == "litter"]
            garbage_coverage = cls._coverage(garbage, image_width, image_height)
            litter_coverage = cls._coverage(litter, image_width, image_height)
            top = max(accepted, key=lambda item: float(item.get("confidence", 0)))

            return ClassificationSummary(
                label=top["class"],
                confidence=float(top.get("confidence", 0)),
                status="classified",
                bbox=cls._to_bbox(top),
                disposition=cls._decide_disposition(
                    garbage_count=len(garbage),
                    litter_count=len(litter),
                    litter_coverage=litter_coverage,
                ),
                garbage_coverage=garbage_coverage,
                litter_coverage=litter_coverage,
                garbage_count=len(garbage),
                litter_count=len(litter),
                detections=[
                    {
                        "class": detection["class"],
                        "confidence": float(detection.get("confidence", 0)),
                        **cls._to_bbox(detection),
                    }
                    for detection in accepted
                ],
            )

        if supported:
            top = max(supported, key=lambda item: float(item.get("confidence", 0)))
            return ClassificationSummary(
                label=top["class"],
                confidence=float(top.get("confidence", 0)),
                status="low-confidence",
                bbox=cls._to_bbox(top),
                disposition=None,
            )

        return ClassificationSummary(
            label="not-garbage",
            confidence=0.0,
            status="classified",
            bbox=None,
            disposition="not-garbage",
        )
