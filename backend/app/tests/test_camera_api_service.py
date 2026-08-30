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

from app.services.camera_api import CameraApiAuthClient, CameraApiError, CameraApiService


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _frame(index):
    return {
        "id": f"frame-{index}",
        "lon": 7.2 + index,
        "lat": 51.4,
        "heading": 90,
        "capturedAt": "2025-01-01T10:00:00Z",
        "imageUrl": f"https://example.com/{index}.jpg",
    }


def test_auth_client_requires_credentials(monkeypatch):
    monkeypatch.delenv("CAMERA_API_EMAIL", raising=False)
    monkeypatch.delenv("CAMERA_API_PASSWORD", raising=False)

    with pytest.raises(CameraApiError):
        CameraApiAuthClient()


def test_auth_client_caches_token(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(kwargs.get("json"))
        return FakeResponse({"accessToken": "token-1"})

    monkeypatch.setattr("app.services.camera_api.requests.post", fake_post)

    client = CameraApiAuthClient(email="a@b.com", password="secret")
    assert client.get_token() == "token-1"
    assert client.get_token() == "token-1"
    assert len(calls) == 1


def test_auth_client_force_refresh_relogs_in(monkeypatch):
    tokens = iter(["token-1", "token-2"])
    monkeypatch.setattr(
        "app.services.camera_api.requests.post",
        lambda *args, **kwargs: FakeResponse({"accessToken": next(tokens)}),
    )

    client = CameraApiAuthClient(email="a@b.com", password="secret")
    assert client.get_token() == "token-1"
    assert client.get_token(force_refresh=True) == "token-2"


def test_fetch_frame_batch_maps_content_and_cursor(monkeypatch):
    auth = CameraApiAuthClient(email="a@b.com", password="secret")
    monkeypatch.setattr(auth, "get_token", lambda force_refresh=False: "token-1")

    def fake_get(*args, **kwargs):
        assert kwargs["headers"]["Authorization"] == "Bearer token-1"
        return FakeResponse(
            {
                "content": [_frame(0), _frame(1)],
                "nextCursor": "cursor-2",
                "hasNext": True,
            }
        )

    monkeypatch.setattr("app.services.camera_api.requests.get", fake_get)

    service = CameraApiService(auth=auth)
    frames, next_cursor = service.fetch_frame_batch(size=2)

    assert len(frames) == 2
    assert frames[0]["id"] == "frame-0"
    assert frames[0]["latitude"] == 51.4
    assert next_cursor == "cursor-2"


def test_fetch_frame_batch_no_next_cursor_when_exhausted(monkeypatch):
    auth = CameraApiAuthClient(email="a@b.com", password="secret")
    monkeypatch.setattr(auth, "get_token", lambda force_refresh=False: "token-1")
    monkeypatch.setattr(
        "app.services.camera_api.requests.get",
        lambda *args, **kwargs: FakeResponse(
            {"content": [_frame(0)], "nextCursor": None, "hasNext": False}
        ),
    )

    service = CameraApiService(auth=auth)
    _, next_cursor = service.fetch_frame_batch(size=1)

    assert next_cursor is None


def test_fetch_frame_batch_relogs_in_on_401(monkeypatch):
    auth = CameraApiAuthClient(email="a@b.com", password="secret")
    tokens = iter(["stale-token", "fresh-token"])
    monkeypatch.setattr(
        auth, "get_token", lambda force_refresh=False: next(tokens)
    )

    responses = iter(
        [
            FakeResponse({}, status_code=401),
            FakeResponse(
                {"content": [_frame(0)], "nextCursor": None, "hasNext": False}
            ),
        ]
    )
    monkeypatch.setattr(
        "app.services.camera_api.requests.get",
        lambda *args, **kwargs: next(responses),
    )

    service = CameraApiService(auth=auth)
    frames, _ = service.fetch_frame_batch(size=1)

    assert len(frames) == 1


def test_reverse_geocode_uses_cache(monkeypatch):
    calls = []

    def fake_get(*args, **kwargs):
        calls.append(kwargs.get("params"))
        return FakeResponse({"address": {"city": "Bochum", "country": "Germany"}})

    monkeypatch.setattr("app.services.camera_api.requests.get", fake_get)

    service = CameraApiService(
        auth=CameraApiAuthClient(email="a@b.com", password="secret")
    )
    first = service.reverse_geocode(51.4818, 7.2162)
    second = service.reverse_geocode(51.4818, 7.2162)

    assert first == ("Bochum", "Germany")
    assert second == ("Bochum", "Germany")
    assert len(calls) == 1
