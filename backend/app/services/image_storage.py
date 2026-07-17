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
