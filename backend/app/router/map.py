from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/map", tags=["map"])


class MapRequest(BaseModel):
    city: str
    country: str


class DumpData(BaseModel):
    id: int
    city: str
    country: str
    latitude: float
    longitude: float
    type: str
    confidence: float
    description: str


@router.post("/dump-data", response_model=List[DumpData])
def get_dump_data(payload: MapRequest):
    # dummy date for now
    return [
        DumpData(
            id=1,
            city=payload.city,
            country=payload.country,
            latitude=51.4818,
            longitude=7.2162,
            type="fly_dump",
            confidence=0.92,
            description="Detected possible illegal dumping site.",
        ),
        DumpData(
            id=2,
            city=payload.city,
            country=payload.country,
            latitude=51.4851,
            longitude=7.2208,
            type="weed",
            confidence=0.81,
            description="Detected possible overgrown vegetation.",
        ),
    ]