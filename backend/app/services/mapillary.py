import os

import requests


class MapillaryImportError(RuntimeError):
    pass


class MapillaryService:
    GEOCODING_URL = "https://nominatim.openstreetmap.org/search"
    IMAGES_URL = "https://graph.mapillary.com/images"
    MAX_BBOX_AREA = 0.0001
    MAX_CANDIDATE_IMAGES = 1000

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token or os.getenv("MAPILLARY_ACCESS_TOKEN")
        if not self.access_token:
            raise MapillaryImportError("MAPILLARY_ACCESS_TOKEN is not configured.")

    def fetch_city_images(self, city: str, limit: int) -> list[dict]:
        images, _ = self.fetch_city_image_batch(city, limit)
        return images

    def fetch_city_image_batch(
        self,
        city: str,
        limit: int,
        pagination_next: str | None = None,
    ) -> tuple[list[dict], str | None]:
        bbox = self._geocode_german_city(city)
        offset = 0
        if pagination_next and pagination_next.startswith("offset:"):
            try:
                offset = max(0, int(pagination_next.split(":", 1)[1]))
            except ValueError as exc:
                raise MapillaryImportError(
                    "Invalid Mapillary pagination value."
                ) from exc

        requested_limit = min(
            offset + limit + 1,
            self.MAX_CANDIDATE_IMAGES,
        )

        params = {
            "bbox": ",".join(str(value) for value in bbox),
            "fields": "id,geometry,thumb_1024_url,captured_at",
            "limit": requested_limit,
        }

        response = requests.get(
            self.IMAGES_URL,
            params=params,
            headers={"Authorization": f"OAuth {self.access_token}"},
            timeout=60,
        )
        response.raise_for_status()

        payload = response.json()
        raw_items = payload.get("data", [])
        selected_items = raw_items[offset:offset + limit]
        images = []
        for item in selected_items:
            coordinates = item.get("geometry", {}).get("coordinates", [])
            image_url = item.get("thumb_1024_url")
            if len(coordinates) < 2 or not image_url:
                continue
            images.append(
                {
                    "id": str(item["id"]),
                    "image_url": image_url,
                    "longitude": float(coordinates[0]),
                    "latitude": float(coordinates[1]),
                }
            )
        next_offset = offset + len(selected_items)
        has_more = (
            len(selected_items) == limit
            and len(raw_items) > next_offset
            and requested_limit < self.MAX_CANDIDATE_IMAGES
        )
        pagination_next = f"offset:{next_offset}" if has_more else None
        return images, pagination_next

    def download_image(self, image_url: str) -> bytes:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        return response.content

    def _geocode_german_city(self, city: str) -> tuple[float, float, float, float]:
        response = requests.get(
            self.GEOCODING_URL,
            params={
                "q": city,
                "format": "jsonv2",
                "countrycodes": "de",
                "limit": 1,
            },
            headers={"User-Agent": "Zolitron-MVP/1.0"},
            timeout=30,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            raise MapillaryImportError(f"No German city was found for '{city}'.")

        south, north, west, east = (
            float(value) for value in results[0]["boundingbox"]
        )
        return self._limit_bbox_area(west, south, east, north)

    def _limit_bbox_area(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
    ) -> tuple[float, float, float, float]:
        width = east - west
        height = north - south
        area = width * height
        if area <= self.MAX_BBOX_AREA:
            return west, south, east, north

        scale = (self.MAX_BBOX_AREA / area) ** 0.5
        half_width = width * scale / 2
        half_height = height * scale / 2
        center_longitude = (west + east) / 2
        center_latitude = (south + north) / 2
        return (
            center_longitude - half_width,
            center_latitude - half_height,
            center_longitude + half_width,
            center_latitude + half_height,
        )
