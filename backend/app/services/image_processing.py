# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zolitron
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
from dataclasses import dataclass, field
from typing import NamedTuple

from PIL import Image as PillowImage
from sqlalchemy.orm import Session

from app.repositories.image_processing import ImageProcessingRepository
from app.schemas.api import ClassificationRead
from app.services.catalog import CatalogService
from app.services.detection import CONFIDENCE_THRESHOLDS, DetectionService
from app.services.image_storage import LocalImageStorage

# MVP calibration values, all provisional and to be re-tuned against labelled
# images. Street-camera frames are mostly sky, roofline and distant road, so
# coverage is measured against the actionable ground region rather than the
# whole frame: everything below GROUND_REGION_TOP of the frame height.
GROUND_REGION_TOP = 0.40  # fraction of frame height treated as non-actionable
MIN_DETECTION_COVERAGE = 0.005  # below this ground fraction a box is model noise
GARBAGE_COLLECT_COVERAGE = 0.02  # lone garbage at/above this ground share: collect
GARBAGE_COLLECT_COUNT = 2  # ...or this many corroborating garbage boxes
LITTER_COLLECT_COVERAGE = 0.05
LITTER_COLLECT_COUNT = 6


class ImageValidationError(ValueError):
    pass


@dataclass
class ClassificationSummary:
    """Everything one image's accepted detections say about it.

    The two coverage fields are ground-region coverage: the share of the
    actionable region below the horizon line that the class's surviving boxes
    take up, not the share of the whole frame.
    """

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


class StoreAndClassifyResult(NamedTuple):
    """What one `store_and_classify` call did, not just what it produced.

    `created` is False when the call short-circuited on content already in the
    catalogue — the SHA-256 storage path matched an existing classification, or
    an existing image row was reused rather than a new one written. Callers
    that batch-import need that distinction to report duplicates instead of
    silently counting them as fresh work.
    """

    classification: ClassificationRead
    created: bool


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
    ) -> StoreAndClassifyResult:
        city = self.validate_city(city)
        extension = self.validate_image(content)
        width, height = self.read_image_dimensions(content)
        stored = self.storage.save(content, extension, namespace)

        existing = self.repository.get_classification_by_storage_path(
            stored.storage_path
        )
        if existing:
            # Same bytes, same SHA-256 storage path: already in the catalogue.
            return StoreAndClassifyResult(
                CatalogService(self.db).classification_to_schema(existing),
                created=False,
            )

        image = self.repository.get_image_by_storage_path(stored.storage_path)
        created = image is None
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

        return StoreAndClassifyResult(
            CatalogService(self.db).classification_to_schema(classification),
            created=created,
        )

    @staticmethod
    def _to_bbox(detection: dict) -> dict:
        return {
            "x": detection.get("x"),
            "y": detection.get("y"),
            "width": detection.get("width"),
            "height": detection.get("height"),
        }

    @staticmethod
    def _ground_coverage(
        detection: dict,
        image_width: int | None,
        image_height: int | None,
    ) -> float:
        """One box's share of the actionable ground region.

        The ground region is the full-width rectangle below
        `GROUND_REGION_TOP` of the frame height. The box is intersected with
        that rectangle, so a box sitting entirely in the sky clips to zero and
        a box straddling the horizon line only contributes its lower part.
        """
        frame_width = float(image_width or 0)
        frame_height = float(image_height or 0)
        ground_area = frame_width * frame_height * (1.0 - GROUND_REGION_TOP)
        if ground_area <= 0:
            return 0.0

        box_width = float(detection.get("width") or 0)
        box_height = float(detection.get("height") or 0)
        centre_x = float(detection.get("x") or 0)
        centre_y = float(detection.get("y") or 0)

        left = centre_x - box_width / 2
        right = centre_x + box_width / 2
        top = centre_y - box_height / 2
        bottom = centre_y + box_height / 2

        ground_line = frame_height * GROUND_REGION_TOP
        clipped_width = max(0.0, min(right, frame_width) - max(left, 0.0))
        clipped_height = max(0.0, min(bottom, frame_height) - max(top, ground_line))
        return (clipped_width * clipped_height) / ground_area

    @staticmethod
    def _total_coverage(coverages: list[float]) -> float:
        """Summed ground coverage, clamped where boxes overlap."""
        return min(sum(coverages), 1.0)

    @classmethod
    def _decide_disposition(
        cls,
        *,
        garbage_count: int,
        garbage_coverage: float,
        litter_count: int,
        litter_coverage: float,
    ) -> str:
        """Size or corroboration earns a collection; a lone small box is watched.

        Garbage escalates on a lower bar than litter, but is no longer an
        automatic collection: a single small garbage box now reads as `watch`.
        """
        if garbage_count >= 1:
            if (
                garbage_coverage >= GARBAGE_COLLECT_COVERAGE
                or garbage_count >= GARBAGE_COLLECT_COUNT
            ):
                return "collect"
            return "watch"
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
            # Boxes too small to matter on the ground are model noise on
            # hedges and pavement: they clear the confidence filter but never
            # reach the rule, and are not persisted as detection rows.
            scored = [
                (detection, cls._ground_coverage(detection, image_width, image_height))
                for detection in accepted
            ]
            survivors = [
                (detection, coverage)
                for detection, coverage in scored
                if coverage >= MIN_DETECTION_COVERAGE
            ]

            if not survivors:
                top = max(accepted, key=lambda item: float(item.get("confidence", 0)))
                return ClassificationSummary(
                    label=top["class"],
                    confidence=float(top.get("confidence", 0)),
                    status="classified",
                    bbox=None,
                    disposition="not-garbage",
                )

            garbage = [item for item in survivors if item[0].get("class") == "garbage"]
            litter = [item for item in survivors if item[0].get("class") == "litter"]
            garbage_coverage = cls._total_coverage([item[1] for item in garbage])
            litter_coverage = cls._total_coverage([item[1] for item in litter])
            top = max(
                survivors, key=lambda item: float(item[0].get("confidence", 0))
            )[0]

            return ClassificationSummary(
                label=top["class"],
                confidence=float(top.get("confidence", 0)),
                status="classified",
                bbox=cls._to_bbox(top),
                disposition=cls._decide_disposition(
                    garbage_count=len(garbage),
                    garbage_coverage=garbage_coverage,
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
                    for detection, _ in survivors
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
