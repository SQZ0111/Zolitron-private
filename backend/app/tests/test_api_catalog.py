from app.db import Base
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_normalized_tables_exist_in_metadata():
    expected_tables = {
        "images",
        "classifications",
        "labels",
        "categories",
        "analysis_runs",
    }

    assert expected_tables.issubset(set(Base.metadata.tables.keys()))


def test_images_endpoint_returns_dummy_images_with_img_url():
    response = client.get("/api/images")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 4
    assert "imgUrl" in data[0]
    assert data[0]["country"] == "Germany"


def test_classifications_endpoint_returns_marker_ready_data():
    response = client.get("/api/classifications")

    assert response.status_code == 200
    data = response.json()
    labels = {item["label"] for item in data}

    assert {"overgrown", "not-overgrown", "garbage", "not-garbage"}.issubset(labels)
    assert all("imgUrl" in item for item in data)
    assert all("latitude" in item for item in data)
    assert all("longitude" in item for item in data)


def test_classifications_can_filter_by_city_and_label():
    response = client.get("/api/classifications", params={"city": "Bochum", "label": "garbage"})

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["city"] == "Bochum"
    assert data[0]["label"] == "garbage"


def test_labels_and_categories_endpoints_return_json():
    labels_response = client.get("/api/labels")
    categories_response = client.get("/api/labels/categories")

    assert labels_response.status_code == 200
    assert categories_response.status_code == 200
    assert len(labels_response.json()) >= 4
    assert len(categories_response.json()) >= 2


def test_stats_endpoint_returns_counts():
    response = client.get("/api/stats")

    assert response.status_code == 200
    data = response.json()

    assert data["image_count"] >= 4
    assert data["classification_count"] >= 4
    assert data["classifications_by_label"]["garbage"] == 1


def test_missing_image_uses_safe_error_schema():
    response = client.get("/api/images/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Image not found.",
        "code": "IMAGE_NOT_FOUND",
    }
