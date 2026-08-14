from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import ApiError, ClassificationRead, ImageRead
from app.schemas.image_processing import (
    CameraFrameBatchImportRequest,
    CameraFrameBatchJobStartResponse,
    CameraFrameBatchJobStatusResponse,
)
from app.services.camera_frame_jobs import camera_frame_batch_jobs
from app.services.catalog import CatalogService
from app.services.detection import RoboflowDetectionError
from app.services.image_processing import ImageProcessingService, ImageValidationError

router = APIRouter(
    prefix="/api/images",
    tags=["images"],
    responses={404: {"model": ApiError}},
)


@router.get("", response_model=list[ImageRead])
def list_images(db: Session = Depends(get_db)):
    return CatalogService(db).list_images()


@router.post("/upload", response_model=ClassificationRead)
def upload_image(
    file: UploadFile = File(...),
    city: str = Form(...),
    country: str = Form(default="Germany"),
    latitude: float | None = Form(default=None),
    longitude: float | None = Form(default=None),
    db: Session = Depends(get_db),
):
    try:
        return ImageProcessingService(db).store_and_classify(
            content=file.file.read(),
            city=city,
            country=country,
            latitude=latitude,
            longitude=longitude,
            source="upload",
            namespace="uploads",
        )
    except ImageValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={"detail": str(exc), "code": "INVALID_IMAGE"},
        ) from exc
    except RoboflowDetectionError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "detail": f"Image classification failed: {exc}",
                "code": "CLASSIFICATION_FAILED",
            },
        ) from exc


@router.post(
    "/import/camera-frames/jobs",
    response_model=CameraFrameBatchJobStartResponse,
    status_code=202,
)
def start_camera_frame_batch_job(
    request: CameraFrameBatchImportRequest,
    background_tasks: BackgroundTasks,
):
    job = camera_frame_batch_jobs.create()
    background_tasks.add_task(camera_frame_batch_jobs.run, job.job_id, request)
    return CameraFrameBatchJobStartResponse(job_id=job.job_id)


@router.get(
    "/import/camera-frames/jobs/{job_id}",
    response_model=CameraFrameBatchJobStatusResponse,
)
def get_camera_frame_batch_job(job_id: str):
    job = camera_frame_batch_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Processing job not found.", "code": "JOB_NOT_FOUND"},
        )
    return CameraFrameBatchJobStatusResponse(
        job_id=job.job_id,
        state=job.state,
        progress=job.progress,
        message=job.message,
        items=job.items,
        cursor=job.cursor,
        error=job.error,
    )


@router.post(
    "/import/camera-frames/jobs/{job_id}/cancel",
    response_model=CameraFrameBatchJobStatusResponse,
)
def cancel_camera_frame_batch_job(job_id: str):
    job = camera_frame_batch_jobs.cancel(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Processing job not found.", "code": "JOB_NOT_FOUND"},
        )
    return CameraFrameBatchJobStatusResponse(
        job_id=job.job_id,
        state=job.state,
        progress=job.progress,
        message=job.message,
        items=job.items,
        cursor=job.cursor,
        error=job.error,
    )


@router.get("/{image_id}", response_model=ImageRead)
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = CatalogService(db).get_image(image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Image not found.", "code": "IMAGE_NOT_FOUND"},
        )
    return image
