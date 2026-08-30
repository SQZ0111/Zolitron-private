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

import logging
import os

import requests

logger = logging.getLogger(__name__)


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

    # The `/camera-frames/dataset` envelope is NOT confirmed against the live
    # API or any published spec: the shapes below are tolerated candidates, and
    # the INFO block logged by `fetch_frame_batch` is what actually settles
    # which of them the server uses.
    CONTENT_KEYS = ("content", "items", "data")
    CURSOR_KEYS = ("nextCursor", "next_cursor", "cursor", "next")
    HAS_NEXT_KEYS = ("hasNext", "has_next", "hasMore")
    PAGE_NUMBER_KEYS = ("number", "page", "pageNumber")
    ITEM_IMAGE_URL_KEYS = ("imageUrl", "image_url", "url")
    ITEM_LONGITUDE_KEYS = ("lon", "longitude")
    ITEM_LATITUDE_KEYS = ("lat", "latitude")
    ITEM_CAPTURED_AT_KEYS = ("capturedAt", "captured_at")
    LOG_VALUE_LIMIT = 200

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
        requested_size = max(1, min(size, self.MAX_SIZE))
        params = {"size": requested_size}
        if cursor:
            params["cursor"] = cursor
        if created_from:
            params["createdFrom"] = created_from
        if created_to:
            params["createdTo"] = created_to

        url = f"{self.data_url}/camera-frames/dataset"
        response = self._authorized_get(url, params)
        payload = response.json()

        raw_items, content_key = self._extract_content(payload)
        frames = [
            frame
            for frame in (self._to_frame(item) for item in raw_items)
            if frame is not None
        ]
        next_cursor, cursor_source = self._resolve_next_cursor(
            payload, len(raw_items), requested_size
        )

        self._log_payload_shape(
            url=getattr(response, "url", None) or url,
            params=params,
            payload=payload,
            raw_items=raw_items,
            content_key=content_key,
            frame_count=len(frames),
            requested_size=requested_size,
            next_cursor=next_cursor,
            cursor_source=cursor_source,
        )
        return frames, next_cursor

    @classmethod
    def _extract_content(cls, payload) -> tuple[list, str]:
        """The page's items, plus the name of the field they came from.

        A bare list payload is a page in itself; otherwise the first of
        `content` / `items` / `data` that actually holds a list wins.
        """
        if isinstance(payload, list):
            return payload, "<bare list>"
        if isinstance(payload, dict):
            for key in cls.CONTENT_KEYS:
                value = payload.get(key)
                if isinstance(value, list):
                    return value, key
        return [], "<none>"

    @staticmethod
    def _item_value(item: dict, keys: tuple[str, ...]):
        for key in keys:
            value = item.get(key)
            if value is not None:
                return value
        return None

    @classmethod
    def _to_frame(cls, item) -> dict | None:
        if not isinstance(item, dict):
            return None
        image_url = cls._item_value(item, cls.ITEM_IMAGE_URL_KEYS)
        longitude = cls._item_value(item, cls.ITEM_LONGITUDE_KEYS)
        latitude = cls._item_value(item, cls.ITEM_LATITUDE_KEYS)
        if image_url is None or longitude is None or latitude is None:
            return None
        try:
            longitude = float(longitude)
            latitude = float(latitude)
        except (TypeError, ValueError):
            return None
        return {
            "id": item.get("id"),
            "image_url": image_url,
            "longitude": longitude,
            "latitude": latitude,
            "heading": item.get("heading"),
            "captured_at": cls._item_value(item, cls.ITEM_CAPTURED_AT_KEYS),
        }

    @classmethod
    def _resolve_next_cursor(
        cls,
        payload,
        item_count: int,
        requested_size: int,
    ) -> tuple[str | None, str]:
        """Work out how (or whether) to ask for the next page.

        Precedence, most explicit signal first:

        1. An explicit gate — the first present of `hasNext` / `has_next` /
           `hasMore` — decides whether there is a next page at all. A present
           but falsy gate ends the walk, whatever else the payload carries.
        2. With no gate present, the page is treated as having a successor only
           if it also came back full. "Full" is `len(items) >= requested size`
           rather than a strict equality, because a server that ignores our
           `size` and serves its own default page still handed us a full page.
        3. The cursor itself is the first present, non-empty of `nextCursor` /
           `next_cursor` / `cursor` / `next`.
        4. Failing a cursor field, a numeric page marker (`number` / `page` /
           `pageNumber`) is advanced by one and returned as a string, so a
           page-number API can be walked through the same cursor parameter.
        """
        if not isinstance(payload, dict):
            return None, "payload is not a mapping"

        gate_key = next((key for key in cls.HAS_NEXT_KEYS if key in payload), None)
        if gate_key is not None and not payload.get(gate_key):
            return None, f"{gate_key}={payload.get(gate_key)!r} reports no further page"

        page_is_full = item_count >= requested_size
        if gate_key is None and not page_is_full:
            return None, (
                f"no has-next field, and the page was not full "
                f"({item_count} of {requested_size})"
            )
        gate_note = (
            f"{gate_key}={payload.get(gate_key)!r}"
            if gate_key is not None
            else f"no has-next field, page full ({item_count} of {requested_size})"
        )

        for key in cls.CURSOR_KEYS:
            value = payload.get(key)
            if value not in (None, "", []):
                return str(value), f"{key} ({gate_note})"

        for key in cls.PAGE_NUMBER_KEYS:
            value = payload.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                continue
            return str(value + 1), f"{key}+1 ({gate_note})"

        return None, f"no cursor or page field present ({gate_note})"

    @classmethod
    def _truncate(cls, text: str) -> str:
        if len(text) <= cls.LOG_VALUE_LIMIT:
            return text
        return f"{text[: cls.LOG_VALUE_LIMIT]}... (+{len(text) - cls.LOG_VALUE_LIMIT} chars)"

    @classmethod
    def _log_payload_shape(
        cls,
        *,
        url: str,
        params: dict,
        payload,
        raw_items: list,
        content_key: str,
        frame_count: int,
        requested_size: int,
        next_cursor: str | None,
        cursor_source: str,
    ) -> None:
        """One INFO record describing what the dataset endpoint really returned.

        The response envelope is unconfirmed, so this block — not the parser —
        is the evidence for what the field names and the `size` parameter
        actually do.
        """
        lines = [
            "camera-frames dataset response",
            f"  request url    : {url}",
            f"  request params : {params}",
            f"  payload type   : {type(payload).__name__}",
        ]
        if isinstance(payload, dict):
            lines.append(f"  payload keys   : {sorted(payload.keys())}")
            for key in sorted(payload.keys()):
                value = payload[key]
                if isinstance(value, list):
                    lines.append(f"    {key} = list(len={len(value)})")
                else:
                    lines.append(f"    {key} = {cls._truncate(repr(value))}")
        elif isinstance(payload, list):
            lines.append(f"  payload        : list(len={len(payload)})")
        else:
            lines.append(f"  payload        : {cls._truncate(repr(payload))}")

        if raw_items and isinstance(raw_items[0], dict):
            lines.append(f"  item[0] keys   : {sorted(raw_items[0].keys())}")
        lines.append(
            f"  content        : from {content_key}, "
            f"{len(raw_items)} item(s) for a requested size of {requested_size}, "
            f"{frame_count} usable frame(s)"
        )
        lines.append(f"  next cursor    : {next_cursor!r} from {cursor_source}")
        logger.info("\n".join(lines))

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
