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

import argparse
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.db import SessionLocal, init_db
from app.models.analysis_run import AnalysisRun
from app.models.classification import Classification
from app.models.detection import Detection
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
        # Bulk deletes skip the ORM cascade, so child rows go first.
        db.query(Detection).delete()
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
