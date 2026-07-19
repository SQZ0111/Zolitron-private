from app.services.mapillary import MapillaryService
from app.schemas.image_processing import MapillaryCityBatchImportRequest


class FakeResponseWithoutPaging:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "data": [
                {
                    "id": str(index),
                    "geometry": {"coordinates": [7.2 + index, 51.4]},
                    "thumb_1024_url": f"https://example.com/{index}.jpg",
                }
                for index in range(3)
            ],
        }


def test_mapillary_batches_use_internal_offset_without_provider_paging(monkeypatch):
    service = MapillaryService(access_token="test-token")
    monkeypatch.setattr(
        service,
        "_geocode_german_city",
        lambda city: (7.1, 51.3, 7.3, 51.5),
    )
    monkeypatch.setattr(
        "app.services.mapillary.requests.get",
        lambda *args, **kwargs: FakeResponseWithoutPaging(),
    )

    first_images, first_pagination_next = service.fetch_city_image_batch(
        "Bochum",
        limit=1,
    )
    second_images, second_pagination_next = service.fetch_city_image_batch(
        "Bochum",
        limit=1,
        pagination_next=first_pagination_next,
    )

    assert first_images[0]["id"] == "0"
    assert first_pagination_next == "offset:1"
    assert second_images[0]["id"] == "1"
    assert second_pagination_next == "offset:2"


def test_batch_request_accepts_pagination_next_alias():
    request = MapillaryCityBatchImportRequest.model_validate(
        {
            "city": "Bochum",
            "country": "Germany",
            "limit": 5,
            "paginationNext": "offset:5",
        }
    )

    assert request.pagination_next == "offset:5"
