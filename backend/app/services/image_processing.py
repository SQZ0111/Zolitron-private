import io

from PIL import Image as PillowImage
from sqlalchemy.orm import Session

from app.repositories.image_processing import ImageProcessingRepository
from app.schemas.api import ClassificationRead
from app.services.catalog import CatalogService
from app.services.detection import CONFIDENCE_THRESHOLDS, DetectionService
from app.services.image_storage import LocalImageStorage


class ImageValidationError(ValueError):
    pass


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
            )
        self.db.commit()

        try:
            detector = self.detector or DetectionService()
            output = detector.detect_trash(stored.absolute_path)
            label, confidence, status = self._summarize_output(output)
            classification = self.repository.create_classification(
                image=image,
                label_name=label,
                confidence=confidence,
                status=status,
                model_version=detector.workflow_id,
            )
        except Exception:
            self.repository.mark_failed(image)
            raise

        return CatalogService(self.db).classification_to_schema(classification)

    @staticmethod
    def _summarize_output(output: dict) -> tuple[str, float, str]:
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
            return (
                "garbage",
                max(float(item.get("confidence", 0)) for item in accepted),
                "classified",
            )
        if supported:
            return (
                "garbage",
                max(float(item.get("confidence", 0)) for item in supported),
                "low-confidence",
            )
        return "not-garbage", 0.0, "classified"
