from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import ClassificationRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/api/map", tags=["map"])


class MapRequest(BaseModel):
    city: str
    country: str


@router.post("/dump-data", response_model=list[ClassificationRead])
def get_dump_data(payload: MapRequest, db: Session = Depends(get_db)):
    return CatalogService(db).list_classifications(city=payload.city)
