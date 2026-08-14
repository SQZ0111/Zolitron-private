import os

import requests


class CameraApiError(RuntimeError):
    pass


class CameraApiAuthClient:
    DEFAULT_ACCOUNT_URL = "https://account-api.zolitron.com"

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        account_url: str | None = None,
    ):
        self.email = email or os.getenv("CAMERA_API_EMAIL")
        self.password = password or os.getenv("CAMERA_API_PASSWORD")
        self.account_url = account_url or os.getenv(
            "CAMERA_API_ACCOUNT_URL", self.DEFAULT_ACCOUNT_URL
        )
        if not self.email or not self.password:
            raise CameraApiError(
                "CAMERA_API_EMAIL and CAMERA_API_PASSWORD environment variables "
                "are not set."
            )
        self._token: str | None = None

    def get_token(self, force_refresh: bool = False) -> str:
        if self._token and not force_refresh:
            return self._token

        response = requests.post(
            f"{self.account_url}/login",
            json={"mail": self.email, "password": self.password},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("accessToken")
        if not token:
            raise CameraApiError("Login response did not contain an accessToken.")

        self._token = token
        return token


class CameraApiService:
    DEFAULT_DATA_URL = "https://rm-api.zolitron.com"
    GEOCODING_URL = "https://nominatim.openstreetmap.org/reverse"
    MAX_SIZE = 1000

    def __init__(
        self,
        auth: CameraApiAuthClient | None = None,
        data_url: str | None = None,
    ):
        self.auth = auth or CameraApiAuthClient()
        self.data_url = data_url or os.getenv("CAMERA_API_DATA_URL", self.DEFAULT_DATA_URL)
        self._city_cache: dict[tuple[float, float], tuple[str, str]] = {}

    def fetch_frame_batch(
        self,
        size: int = 100,
        cursor: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
    ) -> tuple[list[dict], str | None]:
        params = {"size": max(1, min(size, self.MAX_SIZE))}
        if cursor:
            params["cursor"] = cursor
        if created_from:
            params["createdFrom"] = created_from
        if created_to:
            params["createdTo"] = created_to

        response = self._authorized_get(
            f"{self.data_url}/camera-frames/dataset", params
        )
        payload = response.json()

        frames = []
        for item in payload.get("content", []):
            image_url = item.get("imageUrl")
            longitude = item.get("lon")
            latitude = item.get("lat")
            if image_url is None or longitude is None or latitude is None:
                continue
            frames.append(
                {
                    "id": item.get("id"),
                    "image_url": image_url,
                    "longitude": float(longitude),
                    "latitude": float(latitude),
                    "heading": item.get("heading"),
                    "captured_at": item.get("capturedAt"),
                }
            )

        next_cursor = payload.get("nextCursor") if payload.get("hasNext") else None
        return frames, next_cursor

    def download_image(self, image_url: str) -> bytes:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        return response.content

    def reverse_geocode(self, latitude: float, longitude: float) -> tuple[str, str]:
        cache_key = (round(latitude, 3), round(longitude, 3))
        cached = self._city_cache.get(cache_key)
        if cached:
            return cached

        response = requests.get(
            self.GEOCODING_URL,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 10,
            },
            headers={"User-Agent": "Zolitron-MVP/1.0"},
            timeout=30,
        )
        response.raise_for_status()
        address = response.json().get("address", {})

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or "Unknown"
        )
        country = address.get("country", "Germany")

        result = (city, country)
        self._city_cache[cache_key] = result
        return result

    def _authorized_get(self, url: str, params: dict) -> requests.Response:
        token = self.auth.get_token()
        response = requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        if response.status_code == 401:
            token = self.auth.get_token(force_refresh=True)
            response = requests.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60,
            )
        response.raise_for_status()
        return response
