from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import ClassificationRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/api/classifications", tags=["classifications"])


@router.get("", response_model=list[ClassificationRead])
def list_classifications(
    city: str | None = Query(default=None),
    label: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return CatalogService(db).list_classifications(city=city, label=label)
