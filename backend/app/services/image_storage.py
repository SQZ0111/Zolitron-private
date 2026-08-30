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

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredImage:
    absolute_path: str
    storage_path: str
    public_url: str


class LocalImageStorage:
    """Store MVP image files below FastAPI's existing /static mount."""

    def __init__(self, static_root: Path | None = None):
        self.static_root = static_root or Path(__file__).resolve().parents[1] / "static"

    def save(self, content: bytes, extension: str, namespace: str) -> StoredImage:
        digest = hashlib.sha256(content).hexdigest()
        relative_path = Path(namespace) / f"{digest}.{extension}"
        absolute_path = self.static_root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        if not absolute_path.exists():
            absolute_path.write_bytes(content)

        storage_path = relative_path.as_posix()
        return StoredImage(
            absolute_path=str(absolute_path),
            storage_path=storage_path,
            public_url=f"/static/{storage_path}",
        )
