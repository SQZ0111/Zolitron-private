from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import AnalysisRunRead, StatsRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsRead)
def get_stats(db: Session = Depends(get_db)):
    return CatalogService(db).stats()


@router.get("/analysis-runs", response_model=list[AnalysisRunRead])
def list_analysis_runs(db: Session = Depends(get_db)):
    return CatalogService(db).list_analysis_runs()
