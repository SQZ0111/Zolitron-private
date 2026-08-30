# Zolitron Backend API Reference


*Important Note*: This doc is behind. The main city does not correspond to bochum, further dummy-data is not to be used in production. Though the main part of this **supportive** documentation is comprehensional helper.


Developer reference for the FastAPI backend. This file is not part of the architecture report and is not page-limited. The summarised view, with the endpoint table and the core response contract, lives in section 5 of `architecture.md`.

All application routes are mounted under `/api`. Image binaries are served from `/static`. The client reaches the base URL through the `VITE_API_BASE_URL` environment variable and falls back to the local backend URL when it is unset.

Routers are in `backend/app/router/`, schemas in `backend/app/schemas/`, and the application wiring, including the `/static` mount and the exception handlers, in `backend/app/main.py`.

## 1. Classifications

```text
GET /api/classifications
```

Optional query parameters, which may be combined:

| Parameter | Type | Effect |
|---|---|---|
| `city` | string | Restricts results to classifications whose image resolved to that city |
| `label` | string | Restricts results to one label, for example `garbage` or `litter` |

Examples:

```text
GET /api/classifications?city=Bochum
GET /api/classifications?label=garbage
GET /api/classifications?city=Bochum&label=garbage
```

The response is a list of marker-ready classification objects.

```json
[
  {
    "id": 5,
    "image_id": 5,
    "label_id": 5,
    "category_id": 2,
    "analysis_run_id": 1,
    "label": "litter",
    "category": "waste",
    "confidence": 0.71,
    "status": "classified",
    "latitude": 51.4762,
    "longitude": 7.2056,
    "imgUrl": "/static/camera-frames/9f2c.jpg",
    "city": "Bochum",
    "country": "Germany",
    "bbox_x": 512.0,
    "bbox_y": 380.0,
    "bbox_width": 120.0,
    "bbox_height": 90.0,
    "image_width": 1280,
    "image_height": 720,
    "disposition": "watch",
    "garbage_coverage": 0.0,
    "litter_coverage": 0.03,
    "garbage_count": 0,
    "litter_count": 2,
    "detections": [
      {
        "class_name": "litter",
        "confidence": 0.71,
        "bbox_x": 512.0,
        "bbox_y": 380.0,
        "bbox_width": 120.0,
        "bbox_height": 90.0
      }
    ]
  }
]
```

Field notes:

- `status` is `classified` or `low-confidence`. A `low-confidence` row carries a null `disposition`.
- `disposition` is `collect`, `watch`, `not-garbage`, or null.
- The parent `bbox_*` fields hold the highest-confidence surviving box, kept for views written before the child `detections` table existed.
- `garbage_coverage` and `litter_coverage` are shares of the ground region, not of the whole frame.
- `detections` contains one entry per surviving box, meaning one that cleared both the per-class confidence threshold and the noise floor. Boxes dropped as noise are never returned.

The map client calls this endpoint with the `city` parameter only, so both garbage and litter markers arrive and the client decides what to show from the disposition. The server-side `label` filter remains available for other callers. The map refetches when the page opens, after the city is changed through the legend dialog, and after a camera-frame job reports newly processed images.

## 2. Images

```text
GET /api/images
GET /api/images/{image_id}
```

These return image metadata and image URLs for views that need image records without classification detail. `GET /api/images/{image_id}` returns 404 with code `IMAGE_NOT_FOUND` for an unknown id.

## 3. Upload

```text
POST /api/images/upload
```

Multipart form request accepting one JPEG or PNG image.

| Field | Type | Required | Default |
|---|---|---|---|
| `file` | file | yes | none |
| `city` | string | yes | none |
| `country` | string | no | `Germany` |
| `latitude` | float | no | null |
| `longitude` | float | no | null |

The image is validated, deduplicated by SHA-256 content hash, stored under `backend/app/static/uploads`, classified through the Roboflow workflow, and persisted together with its classification and surviving detection rows. The response is the same marker-ready classification object as section 1.

Failures: 400 with code `INVALID_IMAGE` when validation rejects the file; 503 with code `CLASSIFICATION_FAILED` when the remote detection workflow cannot be reached or returns an error.

The upload page supports browsing or dragging multiple photos, sends them as individual requests, and shows persistent dismissible classification notifications.

## 4. Camera-Frame Import Jobs

```text
POST /api/images/import/camera-frames/jobs
GET  /api/images/import/camera-frames/jobs/{job_id}
POST /api/images/import/camera-frames/jobs/{job_id}/cancel
```

### 4.1 Starting a Job

`POST /api/images/import/camera-frames/jobs` starts a background batch import from the camera-frame dataset at `https://rm-api.zolitron.com/camera-frames/dataset` and responds with 202.

Request body:

```json
{
  "size": 5,
  "cursor": null,
  "createdFrom": null,
  "createdTo": null
}
```

| Field | Type | Constraints | Meaning |
|---|---|---|---|
| `size` | int | 1 to 25, default 5 | Number of frames to pull in this batch |
| `cursor` | string or null | default null | Resume point from a previous batch |
| `createdFrom` | string or null | default null | Lower bound on the recording's creation time |
| `createdTo` | string or null | default null | Upper bound on the recording's creation time |

Response:

```json
{ "jobId": "3f8c1d2a-..." }
```

The dataset is a single cursor-paginated stream ordered by the time each recording was added to the system, and it is not scoped by city. Each imported frame is reverse-geocoded from its `lat` and `lon` to resolve a city and country before classification, so city-based map filtering keeps working unchanged. Presigned image URLs expire after roughly an hour, so the job manager re-fetches the same page once if a download fails mid-batch.

Imported binaries are stored under `backend/app/static/camera-frames` and go through the same validation, deduplication, storage, classification, disposition, and persistence path as uploads.

### 4.2 Polling a Job

`GET /api/images/import/camera-frames/jobs/{job_id}` returns the job status.

```json
{
  "jobId": "3f8c1d2a-...",
  "state": "processing",
  "progress": 60,
  "message": "Classifying frame 3 of 5",
  "items": [],
  "cursor": "eyJpZCI6...",
  "error": null
}
```

| Field | Meaning |
|---|---|
| `state` | Lifecycle state, see the table below |
| `progress` | Integer percentage, 0 to 100 |
| `message` | Human-readable progress line for the navbar |
| `items` | Completed classification objects published so far, same shape as section 1 |
| `cursor` | Cursor to pass to the next batch, null when the stream is exhausted |
| `error` | Error text when `state` is `error`, otherwise null |

Job lifecycle states:

| State | Meaning |
|---|---|
| `fetching` | Authenticating and pulling a page of recordings from the data API |
| `validating` | Downloading and validating a frame's binary |
| `processing` | Classifying and persisting frames |
| `stopping` | A cancel was requested and the job is finishing its current frame |
| `stopped` | The job ended early on request |
| `ready` | The batch completed |
| `error` | The batch failed; `error` carries the reason |

Unknown ids return 404 with code `JOB_NOT_FOUND`.

Each completed classification is appended to `items` as soon as it is persisted, so the client can refresh markers while the rest of the batch is still processing.

### 4.3 Cancelling a Job

`POST /api/images/import/camera-frames/jobs/{job_id}/cancel` requests a cooperative stop and returns the same status object. Cancellation is checked between frames, so the job moves to `stopping` and then to `stopped` once the frame in flight finishes. Unknown ids return 404 with code `JOB_NOT_FOUND`.

The navbar's fetch menu starts a batch and stays visible on the map, holding the fetch configuration, progress bar, automatic batching controls, and stop action. It allows 1 to 25 images per batch, supports a maximum number of automatic follow-up batches, and polls the status endpoint to display the backend states above.

## 5. Labels and Categories

```text
GET /api/labels
GET /api/labels/categories
```

These serve filters, legends, and label or category descriptions.

- Current labels: `overgrown`, `not-overgrown`, `garbage`, `not-garbage`, `litter`.
- Current categories: `vegetation`, `waste`.

The active trash-detection pipeline produces `garbage`, `litter`, and `not-garbage` classifications. Vegetation labels remain seeded placeholder data and are not produced by the active workflow.

## 6. Statistics

```text
GET /api/stats
GET /api/stats/analysis-runs
```

`GET /api/stats` returns counts plus four breakdowns.

| Field | Meaning |
|---|---|
| `image_count` | Stored images |
| `classification_count` | Stored classifications |
| `category_count` | Distinct categories |
| `label_count` | Distinct labels |
| `analysis_run_count` | Recorded analysis runs |
| `classifications_by_label` | Counts keyed by label name |
| `classifications_by_category` | Counts keyed by category name |
| `classifications_by_disposition` | Counts keyed by `collect`, `watch`, `not-garbage`, `low-confidence` |
| `classifications_by_city` | Counts keyed by resolved city |

The `low-confidence` key of the disposition breakdown holds the rows stored without a disposition. All breakdowns exclude the seeded dummy rows. The home dashboard reads the disposition breakdown as a donut and the city breakdown as bars.

`GET /api/stats/analysis-runs` returns analysis-run metadata for dashboards and status summaries.

## 7. Direct Classification

```text
POST /api/detections/classify
```

Classifies a single remote image without storing it. Used for model checks and manual testing.

```json
{
  "image_url": "https://example.com/street-image.jpg",
  "city": "Bochum",
  "country": "Germany"
}
```

The response carries the accepted predictions with their bounding boxes, plus `garbage_count`, `litter_count`, and `total_detections`. Nothing is written to the database or to disk. Failures return 400 or 503 in the standard error shape.

## 8. Legacy Map Endpoint

```text
POST /api/map/dump-data
```

```json
{
  "city": "Bochum",
  "country": "Germany"
}
```

Returns the same marker-ready classification list as `GET /api/classifications`, filtered by city. This is a legacy reference route kept for older callers; new client work should use `GET /api/classifications`.

## 9. Static Images

```text
GET /static/dummy-images/{filename}
GET /static/uploads/{filename}
GET /static/camera-frames/{filename}
```

Seeded dummy records reference the example JPG files under `dummy-images`, which makes it possible to verify marker popups locally without running an import. Images created by upload are served from `uploads`, and imported camera frames from `camera-frames`. Filenames are SHA-256 content hashes, so the same binary is stored once regardless of how often it is imported.

## 10. Error Shape

Every failure is normalised into one object.

```json
{
  "detail": "Image not found.",
  "code": "IMAGE_NOT_FOUND"
}
```

The client displays `detail` to users where appropriate and may branch on `code`. Unhandled exceptions, HTTP exceptions, and request validation failures are all mapped into this shape by exception handlers registered on the FastAPI application in `backend/app/main.py`.

Codes currently emitted:

| Code | Status | Raised by |
|---|---|---|
| `INVALID_IMAGE` | 400 | Upload validation rejects the file |
| `IMAGE_NOT_FOUND` | 404 | Unknown image id |
| `JOB_NOT_FOUND` | 404 | Unknown camera-frame job id |
| `CLASSIFICATION_FAILED` | 503 | The remote Roboflow workflow failed |
