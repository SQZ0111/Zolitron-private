from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import CategoryRead, LabelRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/api/labels", tags=["labels"])


@router.get("", response_model=list[LabelRead])
def list_labels(db: Session = Depends(get_db)):
    return CatalogService(db).list_labels()


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return CatalogService(db).list_categories()
