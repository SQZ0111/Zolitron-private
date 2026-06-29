from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import ApiError, ImageRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/api/images", tags=["images"], responses={404: {"model": ApiError}})


@router.get("", response_model=list[ImageRead])
def list_images(db: Session = Depends(get_db)):
    return CatalogService(db).list_images()


@router.get("/{image_id}", response_model=ImageRead)
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = CatalogService(db).get_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail={"detail": "Image not found.", "code": "IMAGE_NOT_FOUND"})
    return image
