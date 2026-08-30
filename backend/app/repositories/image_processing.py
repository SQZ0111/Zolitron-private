from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.models.category import Category
from app.models.classification import Classification
from app.models.detection import Detection
from app.models.image import Image
from app.models.label import Label


class ImageProcessingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_classification_by_storage_path(self, storage_path: str) -> Classification | None:
        return (
            self.db.query(Classification)
            .join(Classification.image)
            .filter(Image.storage_path == storage_path)
            .order_by(Classification.id.desc())
            .first()
        )

    def get_image_by_storage_path(self, storage_path: str) -> Image | None:
        return (
            self.db.query(Image)
            .filter(Image.storage_path == storage_path)
            .order_by(Image.id.desc())
            .first()
        )

    def create_image(
        self,
        *,
        source: str,
        img_url: str,
        storage_path: str,
        city: str,
        country: str,
        latitude: float | None,
        longitude: float | None,
        width: int | None = None,
        height: int | None = None,
    ) -> Image:
        image = Image(
            source=source,
            img_url=img_url,
            storage_path=storage_path,
            city=city,
            country=country,
            latitude=latitude,
            longitude=longitude,
            width=width,
            height=height,
            status="pending",
        )
        self.db.add(image)
        self.db.flush()
        return image

    def prepare_existing_image(
        self,
        image: Image,
        *,
        source: str,
        img_url: str,
        city: str,
        country: str,
        latitude: float | None,
        longitude: float | None,
        width: int | None = None,
        height: int | None = None,
    ) -> Image:
        image.source = source
        image.img_url = img_url
        image.city = city
        image.country = country
        image.latitude = latitude
        image.longitude = longitude
        image.width = width
        image.height = height
        image.status = "pending"
        self.db.flush()
        return image

    def get_or_create_analysis_run(self, model_version: str) -> AnalysisRun:
        run = (
            self.db.query(AnalysisRun)
            .filter(
                AnalysisRun.name == "Roboflow trash detection",
                AnalysisRun.model_version == model_version,
            )
            .first()
        )
        if run:
            return run

        run = AnalysisRun(
            name="Roboflow trash detection",
            status="active",
            model_version=model_version,
        )
        self.db.add(run)
        self.db.flush()
        return run

    def create_classification(
        self,
        *,
        image: Image,
        label_name: str,
        confidence: float,
        status: str,
        model_version: str,
        bbox: dict | None = None,
        disposition: str | None = None,
        garbage_coverage: float | None = None,
        litter_coverage: float | None = None,
        garbage_count: int | None = None,
        litter_count: int | None = None,
        detections: list[dict] | None = None,
    ) -> Classification:
        label = self.db.query(Label).filter(Label.name == label_name).one()
        category = self.db.query(Category).filter(Category.id == label.category_id).one()
        run = self.get_or_create_analysis_run(model_version)
        bbox = bbox or {}

        classification = Classification(
            image_id=image.id,
            label_id=label.id,
            category_id=category.id,
            analysis_run_id=run.id,
            confidence=confidence,
            status=status,
            bbox_x=bbox.get("x"),
            bbox_y=bbox.get("y"),
            bbox_width=bbox.get("width"),
            bbox_height=bbox.get("height"),
            disposition=disposition,
            garbage_coverage=garbage_coverage,
            litter_coverage=litter_coverage,
            garbage_count=garbage_count,
            litter_count=litter_count,
        )
        for detection in detections or []:
            classification.detections.append(
                Detection(
                    class_name=detection.get("class"),
                    confidence=detection.get("confidence"),
                    bbox_x=detection.get("x"),
                    bbox_y=detection.get("y"),
                    bbox_width=detection.get("width"),
                    bbox_height=detection.get("height"),
                )
            )
        image.status = status
        self.db.add(classification)
        self.db.commit()
        self.db.refresh(classification)
        return classification

    def mark_failed(self, image: Image) -> None:
        image.status = "failed"
        self.db.commit()
