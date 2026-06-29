# Zolitron

Zolitron is an MVP web application for detecting and reviewing illegal garbage sites and vegetation/weeds from image data.

Users select a German city or area, the system retrieves or imports image data, classifies images, and visualizes detections on a map for review.

## Tech Stack

- Frontend: Vue 3, Vite, Vuetify, Vue Router, MapLibre GL
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Storage: SQLite for metadata and local disk for image files
- AI/ML: TensorFlow and Pillow for image classification work

## Prerequisites

Install these before cloning/running the project:

- [Node.js](https://nodejs.org/)
- [Python](https://www.python.org/downloads/)

Verify them from a terminal:

```bash
node --version
npm --version
python --version
```

On Windows, the scripts use the Python launcher:

```bash
py -3 --version
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

## Setup From A Fresh Clone

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

## Useful Commands

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
8 passed
```

The backend tests may create a local `backend/zolitron.db` SQLite file. This file is ignored by Git and should not be committed.

## Application Flow

The current MVP is split into three layers: client, backend, and storage. The flowchart below shows the intended request path from the Vue client through the FastAPI backend and into the data/storage layer.

![Zolitron application flowchart](./doc-imgs/flowchart.png)

The flow is:

1. A user opens the Vue client and enters a German city or area on the map page.
2. The map view delegates API communication to the frontend service layer.
3. The FastAPI router receives the request and keeps endpoint logic thin.
4. Backend services handle business rules such as validation, import, deduplication, classification, and review state changes.
5. Repositories isolate SQLite access.
6. Storage utilities handle image files on disk so routers do not access file storage directly.
7. The backend returns detection data to the client.
8. The client renders an empty map after valid location input and later displays classified markers when backend detection data is available.

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

For the MVP, image files are stored on disk and only paths/metadata are stored in SQLite. Do not store raw image blobs in the database.

## Current MVP Direction

The map feature should support:

- Entering a city for map initialization
- Optional street address input for more precise centering
- Restricting searches to Germany
- Explicit validation errors for empty or invalid input
- Rendering an empty map after a valid location submission
- Rendering classified markers from backend results later

Image processing should support:

- Importing images from a source or local folder
- Storing image files on disk
- Storing metadata in SQLite
- Avoiding duplicates
- Tracking processing status

Recommended image statuses:

```text
imported -> pending -> classified -> low-confidence -> reviewed
```

Classification should produce:

- Predicted label
- Confidence score
- Processing status

Initial labels:

- Illegal garbage site
- Vegetation/weeds
- Clean street/no relevant finding

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

