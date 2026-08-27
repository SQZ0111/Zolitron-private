import argparse
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.db import SessionLocal, init_db
from app.models.analysis_run import AnalysisRun
from app.models.classification import Classification
from app.models.image import Image
from app.services.catalog import CatalogService

STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"
NAMESPACES_TO_CLEAR = ["uploads", "camera-frames", "mapillary"]


def clear_static_namespaces() -> None:
    for namespace in NAMESPACES_TO_CLEAR:
        namespace_dir = STATIC_ROOT / namespace
        if namespace_dir.exists():
            shutil.rmtree(namespace_dir)
            namespace_dir.mkdir(parents=True, exist_ok=True)


def reset(reseed: bool) -> None:
    init_db()
    db = SessionLocal()
    try:
        db.query(Classification).delete()
        db.query(Image).delete()
        db.query(AnalysisRun).delete()
        db.commit()

        clear_static_namespaces()

        if reseed:
            CatalogService(db).seed_dummy_data()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wipe all images, classifications, and analysis runs, "
        "plus their stored files under uploads/camera-frames/mapillary."
    )
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="Repopulate the dummy demo data after wiping.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt.",
    )
    args = parser.parse_args()

    if not args.yes:
        answer = input(
            "This deletes every image, classification, and analysis run, "
            "and clears uploads/camera-frames/mapillary. Continue? [y/N] "
        )
        if answer.strip().lower() != "y":
            print("Aborted.")
            raise SystemExit(0)

    reset(reseed=args.reseed)
    print("Database and stored images wiped." + (" Reseeded dummy data." if args.reseed else ""))
