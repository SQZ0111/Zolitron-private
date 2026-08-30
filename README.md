# Zolitron

Zolitron is an MVP web application that finds illegal garbage and litter in German street imagery and shows the accepted detections on a map. Images enter the system either as browser uploads or as background imports from the Zolitron camera fleet's frame API. The backend validates and stores each image, runs it through a remote Roboflow detection workflow, and saves the resulting classification with a `collect` / `watch` / `not-garbage` recommendation. The Vue client renders those results as map markers with image popups, so a reviewer can see at a glance which sites need a collection truck and which only need monitoring. Bochum is the current default focus.

The design rationale, component documentation, and full API reference live in `architecture.md`. Deployment and secrets detail lives in `usage.md`.

## Tech Stack

- Frontend: Vue 3, Vite, Vuetify, Vue Router, MapLibre GL
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Storage: SQLite for metadata, local disk for image files
- AI/ML: Roboflow workflow inference through `inference-sdk`; Pillow for image validation

## Prerequisites

Install these before running the project:

- [Node.js](https://nodejs.org/)
- [Python 3.11 or 3.12](https://www.python.org/downloads/) (`inference-sdk==0.20.0` is not supported by the project's current setup on Python 3.13)

Verify them from a terminal:

```bash
node --version
npm --version
python --version
```

On Windows the scripts use the Python launcher:

```bash
py -3.11 --version
```

## Environment Variables

Create `client/.env` for the frontend:

```env
VITE_MAPTILER_KEY=YOUR_KEY
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Get a MapTiler key from the MapTiler account page: https://cloud.maptiler.com/account/keys

If `VITE_API_BASE_URL` is not set, the client services fall back to the local backend URL.

Create `backend/.env` for the backend:

```env
ROBOFLOW_API_KEY=YOUR_PRIVATE_API_KEY
ROBOFLOW_WORKSPACE=yoav1s-workspace
ROBOFLOW_WORKFLOW_ID=trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2
ROBOFLOW_API_URL=https://serverless.roboflow.com
CAMERA_API_EMAIL=YOUR_ZOLITRON_ACCOUNT_EMAIL
CAMERA_API_PASSWORD=YOUR_ZOLITRON_ACCOUNT_PASSWORD
```

Never commit the Roboflow API key or the camera account credentials. The workspace, workflow ID, and API URLs have application defaults, but keeping them in the environment makes the model and camera source replaceable without changing backend code.

`CAMERA_API_EMAIL` and `CAMERA_API_PASSWORD` are used only by the backend to log in to the Zolitron camera account at `https://account-api.zolitron.com` and fetch camera frames from `https://rm-api.zolitron.com`. They must never be exposed through a `VITE_` client variable. The optional overrides `CAMERA_API_ACCOUNT_URL` and `CAMERA_API_DATA_URL` are available if those endpoints move.

The full list of deployment secrets and their Render placement is documented in `usage.md`.

## Setup

Run all commands from the repository root.

Windows:

```bash
npm install
npm run install:all:win
npm run dev
```

Linux / macOS:

```bash
npm install
npm run install:all:linux
npm run dev:linux
```

The local URLs are:

- Client: http://localhost:5173/
- Backend: http://127.0.0.1:8000
- FastAPI docs: http://127.0.0.1:8000/docs

## Running

Run both frontend and backend:

```bash
npm run dev
```

Windows runs `npm run dev`; Linux and macOS run `npm run dev:linux`.

Run one side only:

```bash
npm run client
npm run backend
npm run backend:linux
```

## Testing

Run tests from the repository root after completing the setup for your OS.

Frontend:

```bash
npm run test:client
```

This runs the Vitest suite in `client/src/tests` and should report:

```text
19 passed
```

Backend on Windows:

```bash
npm run test:backend
```

Backend on Linux / macOS:

```bash
npm run test:backend:linux
```

Either script should report:

```text
27 passed
```

The backend test scripts use the project virtual environment at `backend/venv`. If the venv or its dependencies are missing, run `npm run install:all:win` or `npm run install:all:linux` first.

You can also run pytest directly from the backend directory.

Windows:

```bash
cd backend
.\venv\Scripts\python -m pytest app/tests
```

Linux / macOS:

```bash
cd backend
./venv/bin/python -m pytest app/tests
```

The backend tests may create a local `backend/zolitron.db` SQLite file. It is ignored by Git and should not be committed.

## Resetting Local Data

To wipe all images, classifications, detections, and analysis runs, plus the stored files under `backend/app/static/uploads`, `camera-frames`, and the legacy `mapillary` folder, run this from `backend/` with the virtual environment active:

```bash
./venv/Scripts/python.exe -m app.scripts.reset_db
```

Add `--reseed` to repopulate the dummy demo data afterwards, or `--yes` to skip the confirmation prompt:

```bash
./venv/Scripts/python.exe -m app.scripts.reset_db --reseed --yes
```

Categories and labels are left untouched, since they are fixed taxonomy rather than test data. This is a local CLI tool only.

## CI/CD

The workflow in `.github/workflows/ci-cd.yml` installs the frontend dependencies, runs the frontend tests and build, installs the backend dependencies, runs the backend tests, and publishes a GitHub status check. The repository also carries a Render infrastructure-as-code configuration in `render.yaml` that reads that check before deploying from `main`. The application is not currently deployed; activation is waiting on access to connect the private repository in Render. See `usage.md` for the deployment prerequisites and the required Render environment values.

## Common Problems

### Backend modules are not recognized

Check that the dependencies are installed into the project virtual environment:

```bash
backend\venv\Scripts\python -m pip list
```

On Linux / macOS:

```bash
./backend/venv/bin/python -m pip list
```

Then select the matching interpreter in your IDE, `backend/venv/Scripts/python.exe` on Windows or `backend/venv/bin/python` on Linux and macOS.

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

### Camera-frame import is slow or fails with a geocoding error

Each imported frame is reverse-geocoded through the free Nominatim API, which enforces a rate limit of roughly one request per second and can reject or slow down requests during large or frequent batches. Keep batch sizes reasonable (the UI caps at 25) and avoid running automatic batches back to back without a pause. If imports regularly hit this limit, consider adding a local coordinate cache or switching to a paid geocoding provider.
