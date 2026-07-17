import requests
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import ApiError, ClassificationRead, ImageRead
from app.schemas.image_processing import MapillaryCityImportRequest
from app.services.catalog import CatalogService
from app.services.detection import RoboflowDetectionError
from app.services.image_processing import ImageProcessingService, ImageValidationError
from app.services.mapillary import MapillaryImportError, MapillaryService

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


@router.post("/import/mapillary", response_model=list[ClassificationRead])
def import_mapillary_images(
    request: MapillaryCityImportRequest,
    db: Session = Depends(get_db),
):
    try:
        processor = ImageProcessingService(db)
        mapillary = MapillaryService()
        markers = []
        for source_image in mapillary.fetch_city_images(request.city, request.limit):
            markers.append(
                processor.store_and_classify(
                    content=mapillary.download_image(source_image["image_url"]),
                    city=request.city,
                    country=request.country,
                    latitude=source_image["latitude"],
                    longitude=source_image["longitude"],
                    source="mapillary",
                    namespace="mapillary",
                )
            )
        return markers
    except (ImageValidationError, MapillaryImportError, requests.RequestException) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "The Mapillary city import failed.",
                "code": "MAPILLARY_IMPORT_FAILED",
            },
        ) from exc
    except RoboflowDetectionError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "detail": f"Image classification failed: {exc}",
                "code": "CLASSIFICATION_FAILED",
            },
        ) from exc


@router.get("/{image_id}", response_model=ImageRead)
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = CatalogService(db).get_image(image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Image not found.", "code": "IMAGE_NOT_FOUND"},
        )
    return image
