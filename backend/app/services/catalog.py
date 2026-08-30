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

from sqlalchemy.orm import Session

from app.repositories.catalog import CatalogRepository
from app.schemas.api import ClassificationRead, DetectionRead


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
        return [self.classification_to_schema(item) for item in self.repository.list_classifications(city, label)]

    def stats(self):
        return self.repository.stats()

    def classification_to_schema(self, item):
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
            bbox_x=item.bbox_x,
            bbox_y=item.bbox_y,
            bbox_width=item.bbox_width,
            bbox_height=item.bbox_height,
            image_width=item.image.width,
            image_height=item.image.height,
            disposition=item.disposition,
            garbage_coverage=item.garbage_coverage,
            litter_coverage=item.litter_coverage,
            garbage_count=item.garbage_count,
            litter_count=item.litter_count,
            detections=[
                DetectionRead.model_validate(detection)
                for detection in item.detections
            ],
        )
