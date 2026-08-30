# Usage Guide

You will know about this if you are not a goblin.

## 1. Prerequisites

Before deploying, make sure you have:

- a GitHub repository connected to the project
- a Render account
- access to the team's deployment secrets
- a PostgreSQL database instance or Render database service
- an authorized Roboflow API key for the configured workspace and workflow
- a Zolitron camera account (email/password) with access to the camera-frame dataset

## 2. Required secrets and environment values

Keep secrets in the system that consumes them. Do not commit keys to the repository, documentation, workflow YAML, screenshots, logs, or example files.

### GitHub Actions secrets

The current pipeline requires no GitHub Actions secrets. Render observes the GitHub CI result and deploys after the check passes. The CI jobs do not call the live model, so keep the Roboflow API key out of GitHub Actions unless a separate, explicitly authorized live-model integration job is added later.

### Render backend environment

- `DATABASE_URL`
- `CORS_ORIGINS`
- `ROBOFLOW_API_KEY` — secret value obtained from https://app.roboflow.com/settings/api
- `ROBOFLOW_WORKSPACE` — default: `yoav1s-workspace`
- `ROBOFLOW_WORKFLOW_ID` — default: `trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2`
- `ROBOFLOW_API_URL` — default: `https://serverless.roboflow.com`
- `CAMERA_API_EMAIL` — secret value, the Zolitron camera account's login email
- `CAMERA_API_PASSWORD` — secret value, the Zolitron camera account's login password
- `CAMERA_API_ACCOUNT_URL` — default: `https://account-api.zolitron.com`
- `CAMERA_API_DATA_URL` — default: `https://rm-api.zolitron.com`

Add `ROBOFLOW_API_KEY`, `CAMERA_API_EMAIL`, and `CAMERA_API_PASSWORD` as secret environment variables in Render. Never place their values in `render.yaml`, because that file is committed to Git.

### Render frontend environment

- `VITE_API_BASE_URL`
- `VITE_MAPTILER_KEY`

### Local model key

For local backend development, create `backend/.env`:

```env
ROBOFLOW_API_KEY=YOUR_PRIVATE_API_KEY
ROBOFLOW_WORKSPACE=yoav1s-workspace
ROBOFLOW_WORKFLOW_ID=trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2
ROBOFLOW_API_URL=https://serverless.roboflow.com
CAMERA_API_EMAIL=YOUR_ZOLITRON_ACCOUNT_EMAIL
CAMERA_API_PASSWORD=YOUR_ZOLITRON_ACCOUNT_PASSWORD
```

Use Python 3.11 or 3.12 and install `backend/requirements.txt`. The backend uses the `inference-sdk` module to call the Roboflow serverless workflow; installing the separate `roboflow` module does not replace this dependency.

The camera account credentials are required only for `POST /api/images/import/camera-frames/jobs`. Keep them in `backend/.env`; never expose them through the Vue client.


## Team note

Keep this file private and share it only with authorized team members.
