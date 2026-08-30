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

import pytest

from app.db import Base, SessionLocal
from app.models.analysis_run import AnalysisRun
from app.models.classification import Classification
from app.models.image import Image
from app.models.label import Label


def test_normalized_tables_exist_in_metadata():
    expected_tables = {
        "images",
        "classifications",
        "labels",
        "categories",
        "analysis_runs",
        "detections",
    }

    assert expected_tables.issubset(set(Base.metadata.tables.keys()))


@pytest.fixture(scope="session")
def real_classification(client):
    """A real (non-dummy) image + classification, since seeded dummy data is now excluded from all catalog endpoints."""
    db = SessionLocal()
    try:
        label = db.query(Label).filter(Label.name == "garbage").one()
        run = AnalysisRun(name="Test run", status="completed", model_version="test")
        db.add(run)
        db.flush()

        image = Image(
            source="upload",
            img_url="/static/uploads/test-real.jpg",
            storage_path="uploads/test-real.jpg",
            city="Bochum",
            country="Germany",
            latitude=51.48,
            longitude=7.22,
            status="classified",
        )
        db.add(image)
        db.flush()

        classification = Classification(
            image_id=image.id,
            label_id=label.id,
            category_id=label.category_id,
            analysis_run_id=run.id,
            confidence=0.9,
            status="classified",
        )
        db.add(classification)
        db.commit()
        db.refresh(classification)
        yield classification
    finally:
        db.close()


def test_images_endpoint_excludes_dummy_data(client, real_classification):
    response = client.get("/api/images")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert all(item["source"] != "dummy" for item in data)
    assert any(item["city"] == "Bochum" and "imgUrl" in item for item in data)


def test_classifications_endpoint_returns_marker_ready_data(client, real_classification):
    response = client.get("/api/classifications")

    assert response.status_code == 200
    data = response.json()

    assert all("imgUrl" in item for item in data)
    assert all("latitude" in item for item in data)
    assert all("longitude" in item for item in data)
    assert not any("/dummy-images/" in item["imgUrl"] for item in data)
    assert any(item["label"] == "garbage" and item["city"] == "Bochum" for item in data)


def test_classifications_can_filter_by_city_and_label(client, real_classification):
    response = client.get("/api/classifications", params={"city": "Bochum", "label": "garbage"})

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["city"] == "Bochum"
    assert data[0]["label"] == "garbage"


def test_labels_and_categories_endpoints_return_json(client):
    labels_response = client.get("/api/labels")
    categories_response = client.get("/api/labels/categories")

    assert labels_response.status_code == 200
    assert categories_response.status_code == 200
    assert len(labels_response.json()) >= 5
    assert len(categories_response.json()) >= 2

    label_names = {item["name"] for item in labels_response.json()}
    assert {"garbage", "litter", "not-garbage"}.issubset(label_names)


def test_stats_endpoint_excludes_dummy_data(client, real_classification):
    response = client.get("/api/stats")

    assert response.status_code == 200
    data = response.json()

    assert data["image_count"] >= 1
    assert data["classification_count"] >= 1
    assert data["classifications_by_label"]["garbage"] >= 1
    assert data["classifications_by_category"]["waste"] >= 1


def test_stats_breaks_classifications_down_by_disposition_and_city(client, real_classification):
    response = client.get("/api/stats")

    assert response.status_code == 200
    data = response.json()

    by_disposition = data["classifications_by_disposition"]
    by_city = data["classifications_by_city"]

    assert set(by_disposition) <= {"collect", "watch", "not-garbage", "low-confidence"}
    # The fixture row stores no disposition, so it lands in the low-confidence bucket.
    assert by_disposition["low-confidence"] >= 1
    assert sum(by_disposition.values()) == data["classification_count"]

    assert by_city["Bochum"] >= 1
    # Dummy rows are Bochum too, so a matching total proves they are excluded.
    assert sum(by_city.values()) == data["classification_count"]


def test_missing_image_uses_safe_error_schema(client):
    response = client.get("/api/images/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Image not found.",
        "code": "IMAGE_NOT_FOUND",
    }
