from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.analysis_run import AnalysisRun
from app.models.category import Category
from app.models.classification import Classification
from app.models.image import Image
from app.models.label import Label

DUMMY_CATEGORIES = [
    {"id": 1, "name": "vegetation", "description": "Vegetation and overgrowth review category."},
    {"id": 2, "name": "waste", "description": "Garbage and illegal dumping review category."},
]

DUMMY_LABELS = [
    {"id": 1, "name": "overgrown", "description": "Vegetation or weeds detected.", "category_id": 1},
    {"id": 2, "name": "not-overgrown", "description": "No relevant vegetation detected.", "category_id": 1},
    {"id": 3, "name": "garbage", "description": "Garbage or illegal dumping detected.", "category_id": 2},
    {"id": 4, "name": "not-garbage", "description": "No garbage detected.", "category_id": 2},
]

DUMMY_IMAGES = [
    {
        "id": 1,
        "source": "dummy",
        "img_url": "/static/dummy-images/overgrown-1.jpg",
        "storage_path": "dummy-images/overgrown-1.jpg",
        "city": "Bochum",
        "country": "Germany",
        "latitude": 51.4818,
        "longitude": 7.2162,
        "status": "classified",
    },
    {
        "id": 2,
        "source": "dummy",
        "img_url": "/static/dummy-images/overgrown-2.jpg",
        "storage_path": "dummy-images/overgrown-2.jpg",
        "city": "Bochum",
        "country": "Germany",
        "latitude": 51.4851,
        "longitude": 7.2208,
        "status": "classified",
    },
    {
        "id": 3,
        "source": "dummy",
        "img_url": "/static/dummy-images/not-overgrown-1.jpg",
        "storage_path": "dummy-images/not-overgrown-1.jpg",
        "city": "Bochum",
        "country": "Germany",
        "latitude": 51.4787,
        "longitude": 7.2294,
        "status": "classified",
    },
    {
        "id": 4,
        "source": "dummy",
        "img_url": "/static/dummy-images/not-garbage-1.jpg",
        "storage_path": "dummy-images/not-garbage-1.jpg",
        "city": "Bochum",
        "country": "Germany",
        "latitude": 51.4903,
        "longitude": 7.2113,
        "status": "classified",
    },
    {
        "id": 5,
        "source": "dummy",
        "img_url": "/static/dummy-images/mixed-review-1.jpg",
        "storage_path": "dummy-images/mixed-review-1.jpg",
        "city": "Bochum",
        "country": "Germany",
        "latitude": 51.4762,
        "longitude": 7.2056,
        "status": "low-confidence",
    },
]

DUMMY_ANALYSIS_RUN = {
    "id": 1,
    "name": "Dummy marker data",
    "status": "completed",
    "model_version": "dummy-v1",
}

DUMMY_CLASSIFICATIONS = [
    {"id": 1, "image_id": 1, "label_id": 1, "category_id": 1, "analysis_run_id": 1, "confidence": 0.91, "status": "classified"},
    {"id": 2, "image_id": 2, "label_id": 1, "category_id": 1, "analysis_run_id": 1, "confidence": 0.86, "status": "classified"},
    {"id": 3, "image_id": 3, "label_id": 2, "category_id": 1, "analysis_run_id": 1, "confidence": 0.79, "status": "classified"},
    {"id": 4, "image_id": 4, "label_id": 4, "category_id": 2, "analysis_run_id": 1, "confidence": 0.84, "status": "classified"},
    {"id": 5, "image_id": 5, "label_id": 3, "category_id": 2, "analysis_run_id": 1, "confidence": 0.57, "status": "low-confidence"},
]


class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def seed_dummy_data(self) -> None:
        for item in DUMMY_CATEGORIES:
            self.db.merge(Category(**item))
        for item in DUMMY_LABELS:
            self.db.merge(Label(**item))
        for item in DUMMY_IMAGES:
            self.db.merge(Image(**item))

        self.db.merge(AnalysisRun(**DUMMY_ANALYSIS_RUN))

        for item in DUMMY_CLASSIFICATIONS:
            self.db.merge(Classification(**item))

        self.db.commit()

    def list_images(self) -> list[Image]:
        return self.db.query(Image).order_by(Image.id).all()

    def get_image(self, image_id: int) -> Image | None:
        return self.db.query(Image).filter(Image.id == image_id).first()

    def list_categories(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.id).all()

    def list_labels(self) -> list[Label]:
        return (
            self.db.query(Label)
            .options(joinedload(Label.category))
            .order_by(Label.id)
            .all()
        )

    def list_analysis_runs(self) -> list[AnalysisRun]:
        return self.db.query(AnalysisRun).order_by(AnalysisRun.id).all()

    def list_classifications(self, city: str | None = None, label: str | None = None) -> list[Classification]:
        query = (
            self.db.query(Classification)
            .options(
                joinedload(Classification.image),
                joinedload(Classification.label),
                joinedload(Classification.category),
            )
            .join(Classification.image)
            .join(Classification.label)
        )

        if city:
            query = query.filter(func.lower(Image.city) == city.lower())
        if label:
            query = query.filter(func.lower(Label.name) == label.lower())

        return query.order_by(Classification.id).all()

    def stats(self) -> dict:
        by_label = dict(
            self.db.query(Label.name, func.count(Classification.id))
            .join(Classification, Classification.label_id == Label.id)
            .group_by(Label.name)
            .all()
        )
        by_category = dict(
            self.db.query(Category.name, func.count(Classification.id))
            .join(Classification, Classification.category_id == Category.id)
            .group_by(Category.name)
            .all()
        )

        return {
            "image_count": self.db.query(Image).count(),
            "classification_count": self.db.query(Classification).count(),
            "category_count": self.db.query(Category).count(),
            "label_count": self.db.query(Label).count(),
            "analysis_run_count": self.db.query(AnalysisRun).count(),
            "classifications_by_label": by_label,
            "classifications_by_category": by_category,
        }




