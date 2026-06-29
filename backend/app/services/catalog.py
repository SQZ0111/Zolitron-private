from sqlalchemy.orm import Session

from app.repositories.catalog import CatalogRepository
from app.schemas.api import ClassificationRead


class CatalogService:
    def __init__(self, db: Session):
        self.repository = CatalogRepository(db)

    def seed_dummy_data(self) -> None:
        self.repository.seed_dummy_data()

    def list_images(self):
        return self.repository.list_images()

    def get_image(self, image_id: int):
        return self.repository.get_image(image_id)

    def list_categories(self):
        return self.repository.list_categories()

    def list_labels(self):
        return self.repository.list_labels()

    def list_analysis_runs(self):
        return self.repository.list_analysis_runs()

    def list_classifications(self, city: str | None = None, label: str | None = None) -> list[ClassificationRead]:
        return [self._classification_to_schema(item) for item in self.repository.list_classifications(city, label)]

    def stats(self):
        return self.repository.stats()

    def _classification_to_schema(self, item):
        return ClassificationRead(
            id=item.id,
            image_id=item.image_id,
            label_id=item.label_id,
            category_id=item.category_id,
            analysis_run_id=item.analysis_run_id,
            label=item.label.name,
            category=item.category.name,
            confidence=item.confidence,
            status=item.status,
            latitude=item.image.latitude,
            longitude=item.image.longitude,
            img_url=item.image.img_url,
            city=item.image.city,
            country=item.image.country,
        )
