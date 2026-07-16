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
