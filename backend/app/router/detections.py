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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import ApiError
from app.schemas.detection import ClassifyImageRequest, ClassifyImageResponse, DetectionPredictionRead
from app.services.detection import DetectionService, RoboflowDetectionError

router = APIRouter(prefix="/api/detections", tags=["detections"], responses={400: {"model": ApiError}, 503: {"model": ApiError}})


@router.post("/classify", response_model=ClassifyImageResponse)
def classify_image(request: ClassifyImageRequest, db: Session = Depends(get_db)):
    """
    Classify an image using the Roboflow trash detection model.

    Args:
        request: Contains image_url and optional location info
        db: Database session (for future classification storage)

    Returns:
        ClassifyImageResponse with predictions and counts
    """
    try:
        service = DetectionService()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "detail": f"Detection service not available: {exc}",
                "code": "DETECTION_SERVICE_UNAVAILABLE"
            }
        )

    try:
        output = service.detect_trash(request.image_url)
    except RoboflowDetectionError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "detail": f"Image classification failed: {exc}",
                "code": "CLASSIFICATION_FAILED"
            }
        )

    counts = service.count_detections(output)
    predictions = service.extract_predictions(output)

    return ClassifyImageResponse(
        predictions=[
            DetectionPredictionRead(
                **{**p, "class": p["class"]}
            )
            for p in predictions
        ],
        garbage_count=counts.get("garbage", 0),
        litter_count=counts.get("litter", 0),
        total_detections=sum(counts.values()),
    )
