# Zolitron

Zolitron is an MVP web application for detecting and reviewing illegal garbage sites and vegetation/weeds from image data.

Users select a German city or area, the system retrieves or imports image data, classifies images, and visualizes detections on a map for review.

## Tech Stack

- Frontend: Vue 3, Vite, Vuetify, Vue Router, MapLibre GL
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Storage: SQLite for metadata and local disk for image files
- AI/ML: Roboflow workflow inference through `inference-sdk`; Pillow is used for image validation

## Prerequisites

Install these before cloning/running the project:

- [Node.js](https://nodejs.org/)
- [Python 3.11 or 3.12](https://www.python.org/downloads/) (`inference-sdk==0.20.0` is not supported by the project's current setup on Python 3.13)

Verify them from a terminal:

```bash
node --version
npm --version
python --version
```

On Windows, the scripts use the Python launcher:

```bash
py -3.11 --version
```

## Environment Variables

To use the map, create a `.env` file in the `client` directory:

```bash
client/.env
```

Add your MapTiler key:

```env
VITE_MAPTILER_KEY=YOUR_KEY
```

You can get a key from the MapTiler account page: https://cloud.maptiler.com/account/keys

To use the trash-detection model locally, create `backend/.env` and add:

```env
ROBOFLOW_API_KEY=YOUR_PRIVATE_API_KEY
ROBOFLOW_WORKSPACE=yoav1s-workspace
ROBOFLOW_WORKFLOW_ID=trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2
ROBOFLOW_API_URL=https://serverless.roboflow.com
MAPILLARY_ACCESS_TOKEN=YOUR_PRIVATE_MAPILLARY_TOKEN
```

Never commit the API key. The workspace, workflow ID, and API URL have application defaults, but keeping them in the environment makes the model replaceable without changing backend code.

`MAPILLARY_ACCESS_TOKEN` is used only by the backend to query georeferenced street images. It must not be exposed through a `VITE_` client variable.

## Model Integration

The current request path is (testable with Postman):

```text
POST /api/detections/classify
  -> detection router
  -> DetectionService
  -> InferenceHTTPClient.run_workflow(...)
  -> Roboflow serverless workflow
  -> confidence filtering and API response mapping
```

Request example:

```json
{
  "image_url": "https://example.com/street-image.jpg",
  "city": "Bochum",
  "country": "Germany"
}
```

The response contains accepted predictions, bounding-box coordinates, `garbage_count`, `litter_count`, and `total_detections`. The service currently applies these per-class confidence thresholds:

- `garbage`: `0.65`
- `litter`: `0.60`

Implemented and reachable now:

- the `/api/detections/classify` route is registered in FastAPI and appears in `/docs`




## Setup

Run commands from the repository root.

### Windows

```bash
npm install
npm run install:all:win
npm run dev
```

### Linux / macOS

```bash
npm install
npm run install:all:linux
npm run dev:linux
```

The local URLs are:

- Client: http://localhost:5173/
- Backend: http://127.0.0.1:8000
- FastAPI docs: http://127.0.0.1:8000/docs

## Starting the app

Run both frontend and backend:

```bash
npm run dev
```

Run frontend only:

```bash
npm run client
```

Run backend only on Windows:

```bash
npm run backend
```

Run backend only on Linux/macOS:

```bash
npm run backend:linux
```

## Testing

Run tests from the repository root after completing the setup for your OS.

## CI/CD and Deployment

This repository includes CI through GitHub Actions and deployment configuration for Render using PostgreSQL. It is not currently deployed: activation is waiting for access to connect and configure the private GitHub repository in Render.

### CI workflow Explaination

[Infrastructure-as-a-service](https://render.com/docs/infrastructure-as-code)

The workflow in [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) will:

- install frontend dependencies
- run frontend tests and build
- install backend dependencies
- run backend tests
- publish a GitHub status check that Render uses before deploying changes from `main`





### Frontend Tests

```bash
npm run test:client
```

This runs the Vitest suite in `client/src/tests`.

### Backend Tests

Windows:

```bash
npm run test:backend
```

Linux/macOS:

```bash
npm run test:backend:linux
```

The backend test scripts use the project virtual environment at `backend/venv`. If the backend venv or dependencies are missing, run the setup command first:

```bash
npm run install:all:win
```

or on Linux/macOS:

```bash
npm run install:all:linux
```

You can also run pytest directly from the backend directory.

Windows:

```bash
cd backend
.\venv\Scripts\python -m pytest app/tests
```

Linux/macOS:

```bash
cd backend
./venv/bin/python -m pytest app/tests
```

Expected backend result for the current suite:

```text
12 passed
```

The backend tests may create a local `backend/zolitron.db` SQLite file. This file is ignored by Git and should not be committed.

## Frontend API Interfaces

Use the backend base URL from the client environment variable when adding frontend service functions:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If `VITE_API_BASE_URL` is not set, frontend services should default to the local backend URL during development.

### Marker / Classification Data

```text
GET /api/classifications
```

Optional query parameters:

```text
city=Bochum
label=garbage
```

Examples:

```text
GET /api/classifications?city=Bochum
GET /api/classifications?label=garbage
GET /api/classifications?city=Bochum&label=garbage
```

Response shape:

```json
[
  {
    "id": 1,
    "image_id": 1,
    "label_id": 1,
    "category_id": 1,
    "analysis_run_id": 1,
    "label": "overgrown",
    "category": "vegetation",
    "confidence": 0.91,
    "status": "classified",
    "latitude": 51.4818,
    "longitude": 7.2162,
    "imgUrl": "/static/dummy-images/overgrown-1.jpg",
    "city": "Bochum",
    "country": "Germany"
  }
]
```

The map client fetches this endpoint when the page opens, after a city search, and after a Mapillary processing job reports newly processed images. Marker rendering is isolated in `client/src/components/Map/ClassificationMarkers.vue`; popups display the classification image, label, category, confidence, status, and location. The marker legend uses purple for garbage/dumping, green for vegetation, and gray for clean or review results.

### Images

```text
GET /api/images
GET /api/images/{image_id}
```

Returns image metadata and image URLs. Use this when a frontend view needs image records without classification details.

### Upload And Mapillary Import

```text
POST /api/images/upload
POST /api/images/import/mapillary
POST /api/images/import/mapillary/batch
POST /api/images/import/mapillary/jobs
GET /api/images/import/mapillary/jobs/{job_id}
POST /api/images/import/mapillary/jobs/{job_id}/cancel
```

`POST /api/images/upload` accepts one multipart JPEG or PNG image plus `city`, `country`, and optional `latitude` and `longitude`. The responsive Vue upload page supports browsing or dragging multiple photos, sends them as individual requests, and shows persistent dismissible classification notifications.
`POST /api/images/import/mapillary` accepts:

```json
{
  "city": "Bochum",
  "country": "Germany",
  "limit": 5
}
```

The upload and standard Mapillary import endpoints store images locally below `backend/app/static/uploads` or `backend/app/static/mapillary`, classify them with the Roboflow workflow, persist image/classification metadata, and return the existing marker-friendly `ClassificationRead` shape.

The navbar's **Fetch sites** menu starts a background batch through `POST /api/images/import/mapillary/jobs`. It allows 1–25 images per batch, supports a maximum number of automatic follow-up batches, and can be stopped cooperatively. The navbar polls `GET /api/images/import/mapillary/jobs/{job_id}` to display the backend's fetching, validating, processing, stopping, ready, and error states.

### Labels And Categories

```text
GET /api/labels
GET /api/labels/categories
```

Use these endpoints if the frontend needs to build filters, legends, or label/category descriptions. The current trash-detection pipeline creates garbage-related classifications. Vegetation labels remain seeded placeholder data and are not produced by the active Roboflow workflow.

Current labels:

```text
overgrown
not-overgrown
garbage
not-garbage
```

Current categories:

```text
vegetation
waste
```

### Statistics

```text
GET /api/stats
GET /api/stats/analysis-runs
```

Use these endpoints for dashboards, counters, or backend status summaries.

### Legacy Map Endpoint

```text
POST /api/map/dump-data
```

Request body:

```json
{
  "city": "Bochum",
  "country": "Germany"
}
```

This currently returns the same marker-ready classification shape as `/api/classifications`, filtered by city. This is a legacy reference route; new client work should use `/api/classifications`.

### Static Popup Images

```text
GET /static/dummy-images/{filename}
```

Example:

```text
GET /static/dummy-images/overgrown-1.jpg
```

Seeded dummy database records reference the example JPG files under this path, so they can be used to verify marker popups locally. Images created by upload or Mapillary import are stored under `/static/uploads/` or `/static/mapillary/`.

### API Errors

All API errors should use this shape:

```json
{
  "detail": "Image not found.",
  "code": "IMAGE_NOT_FOUND"
}
```

Frontend code should display `detail` to users when appropriate and may use `code` for branching or tests.

## Backend Data Interface

Backend route handlers should use service classes instead of calling repositories directly. For the current dummy data/catalog flow, use `CatalogService` from:

```text
backend/app/services/catalog.py
```

Example route-level usage:

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.catalog import CatalogService


def list_classifications(db: Session = Depends(get_db)):
    return CatalogService(db).list_classifications(city="Bochum")
```

The intended dependency direction is:

```text
router -> service -> repository -> database models
```

Use each layer for this purpose:

- `router`: HTTP details only, such as path parameters, query parameters, request body validation, and status codes.
- `service`: business/data interface for the rest of the backend. Add filtering rules, AI result mapping, review logic, and marker response shaping here.
- `repository`: SQLAlchemy queries only. Keep database access here so it can be tested and changed without rewriting route handlers.
- `models`: persisted database entities and relationships.
- `schemas`: response/request contracts for API clients.

Do not import repository classes directly into routers for new work. This keeps route handlers thin and gives backend developers one interface to extend when dummy data is replaced by real image imports or additional model predictions.

Current `CatalogService` methods:

```text
seed_dummy_data()
list_images()
get_image(image_id)
list_categories()
list_labels()
list_analysis_runs()
list_classifications(city=None, label=None)
stats()
```
## Application Flow

The current MVP is split into three layers: client, backend, and storage. The flowchart below shows the intended request path from the Vue client through the FastAPI backend and into the data/storage layer.

![Zolitron application flowchart](./doc-imgs/flowchart.svg)

The flow is:

1. A user opens the Vue client and can choose a German city and Mapillary batch size from the navbar.
2. The Fetch sites menu delegates Mapillary job requests to the frontend image service.
3. The FastAPI router receives the request and keeps endpoint logic thin.
4. Backend services handle business rules such as validation, import, deduplication, classification, and review state changes.
5. Repositories isolate SQLite access.
6. Storage utilities handle image files on disk so routers do not access file storage directly.
7. The backend returns detection data to the client.
8. The navbar reports Mapillary processing progress while the map fetches stored classifications and renders color-coded markers with image popups.

## Architecture Notes

### Client

The client follows a Vue/Vite structure:

```text
client/src/
  views/
  components/
  services/
  router/
  tests/
```

Keep page-level presentation in `views`, reusable UI in `components`, and backend calls in `services`. The map page should orchestrate the experience, while form and marker logic should live in smaller components/services where practical.

### Backend

The backend is a modular FastAPI monolith:

```text
backend/app/
  main.py
  router/
  schemas/
  repositories/
  services/
  models/
  tests/
```

Routers should validate input, call service/repository code, and return response schemas. Business logic such as classification, import, deduplication, and review handling belongs in services, not route handlers.

### Storage

For the MVP, image files are stored on disk and only paths/metadata are stored in SQLite.

## Common Problems

### Backend modules are not recognized

Check that dependencies are installed into the project virtual environment:

```bash
backend\venv\Scripts\python -m pip list
```

On Linux/macOS:

```bash
./backend/venv/bin/python -m pip list
```

Then select the matching interpreter in your IDE:

```text
backend/venv/Scripts/python.exe
```

On Linux/macOS:

```text
backend/venv/bin/python
```

### `concurrently` is not found

Run this once from the repository root:

```bash
npm install
```

### Backend venv is missing

Run the install command for your OS:

```bash
npm run install:all:win
```

or:

```bash
npm run install:all:linux
```

