import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
load_dotenv()

from app.db import SessionLocal, init_db
from app.router import classifications, detections, images, labels, map, stats
from app.services.catalog import CatalogService

logger = logging.getLogger(__name__)

#use lifespan manager for init - https://fastapi.tiangolo.com/advanced/events/

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        CatalogService(db).seed_dummy_data()
    finally:
        db.close()

    yield


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(lifespan=lifespan)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "detail" in exc.detail and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Request failed.", "code": "REQUEST_FAILED"},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request parameters.", "code": "VALIDATION_ERROR"},
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled API error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "code": "INTERNAL_SERVER_ERROR"},
    )


app.include_router(map.router)
app.include_router(images.router)
app.include_router(classifications.router)
app.include_router(detections.router)
app.include_router(labels.router)
app.include_router(stats.router)


@app.get("/")
def read_root():
    return {
        "name": "Zolitron Backend API",
        "status": "running",
        "description": "REST API for Zolitron MVP image metadata and serving as api gateway to client and data services.",
        "docs": {
            "swagger": "/docs",
            "openapi": "/openapi.json",
        },
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/images",
                "description": "List image metadata records, including imgUrl values for marker popups.",
            },
            {
                "method": "GET",
                "path": "/api/images/{image_id}",
                "description": "Get one image metadata record by ID.",
                "example": "/api/images/1",
            },
            {
                "method": "POST",
                "path": "/api/images/upload",
                "description": "Store and classify one uploaded JPEG or PNG image.",
            },
            {
                "method": "POST",
                "path": "/api/images/import/mapillary",
                "description": "Fetch, store, and classify a limited Mapillary sample for a German city.",
                "body_example": {"city": "Bochum", "country": "Germany", "limit": 5},
            },
            {
                "method": "GET",
                "path": "/api/classifications",
                "description": "List marker-ready classification objects with label, category, confidence, coordinates, city, country, and imgUrl.",
                "query_parameters": ["city", "label"],
                "examples": [
                    "/api/classifications?city=Bochum",
                    "/api/classifications?label=garbage",
                    "/api/classifications?city=Bochum&label=garbage",
                ],
            },
            {
                "method": "GET",
                "path": "/api/labels",
                "description": "List available labels and their categories.",
            },
            {
                "method": "GET",
                "path": "/api/labels/categories",
                "description": "List available label categories.",
            },
            {
                "method": "GET",
                "path": "/api/stats",
                "description": "Return image, classification, label, category, and analysis run counts.",
            },
            {
                "method": "GET",
                "path": "/api/stats/analysis-runs",
                "description": "List analysis run metadata.",
            },
            {
                "method": "POST",
                "path": "/api/map/dump-data",
                "description": "Legacy map endpoint returning city-filtered marker-ready classifications.",
                "body_example": {"city": "Bochum", "country": "Germany"},
            },
            {
                "method": "GET",
                "path": "/static/dummy-images/{filename}",
                "description": "Serve dummy marker popup images referenced by imgUrl.",
                "example": "/static/dummy-images/overgrown-1.jpg",
            },
        ],
        "error_schema": {"detail": "string", "code": "string"},
    }
