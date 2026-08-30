import logging
from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4

import requests

from app.db import SessionLocal
from app.schemas.api import ClassificationRead
from app.schemas.image_processing import CameraFrameBatchImportRequest
from app.services.camera_api import CameraApiService
from app.services.image_processing import ImageProcessingService
#error handle logger 
logger = logging.getLogger(__name__)


@dataclass
class CameraFrameBatchJob:
    job_id: str
    state: str = "queued"
    progress: int = 0
    message: str = "Waiting to start"
    items: list[ClassificationRead] = field(default_factory=list)
    cursor: str | None = None
    new_count: int = 0
    duplicate_count: int = 0
    error: str | None = None
    cancel_requested: bool = False


class CameraFrameBatchJobManager:
    """Track local MVP batch jobs so the client can display backend progress."""

    def __init__(self):
        self._jobs: dict[str, CameraFrameBatchJob] = {}
        self._lock = Lock()

    def create(self) -> CameraFrameBatchJob:
        job = CameraFrameBatchJob(job_id=str(uuid4()))
        with self._lock:
            self._jobs[job.job_id] = job
            if len(self._jobs) > 100:
                oldest_job_id = next(iter(self._jobs))
                self._jobs.pop(oldest_job_id, None)
        return job

    def get(self, job_id: str) -> CameraFrameBatchJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return CameraFrameBatchJob(
                job_id=job.job_id,
                state=job.state,
                progress=job.progress,
                message=job.message,
                items=list(job.items),
                cursor=job.cursor,
                new_count=job.new_count,
                duplicate_count=job.duplicate_count,
                error=job.error,
                cancel_requested=job.cancel_requested,
            )

    def update(self, job_id: str, **changes) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for name, value in changes.items():
                setattr(job, name, value)

    def cancel(self, job_id: str) -> CameraFrameBatchJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            if job.state not in {"ready", "error", "stopped"}:
                job.cancel_requested = True
                job.state = "stopping"
                job.message = "Stopping after the current step"
        return self.get(job_id)

    def _stop_if_requested(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs[job_id]
            if not job.cancel_requested:
                return False
            job.state = "stopped"
            job.message = "Fetching stopped manually"
            job.error = None
            return True

    def run(
        self,
        job_id: str,
        request: CameraFrameBatchImportRequest,
    ) -> None:
        db = SessionLocal()
        try:
            self.update(
                job_id,
                state="fetching",
                progress=5,
                message="Finding camera frames",
            )
            camera_api = CameraApiService()
            source_frames, next_cursor = camera_api.fetch_frame_batch(
                size=request.size,
                cursor=request.cursor,
                created_from=request.created_from,
                created_to=request.created_to,
            )
            if self._stop_if_requested(job_id):
                return

            processor = ImageProcessingService(db)
            items: list[ClassificationRead] = []
            new_count = 0
            duplicate_count = 0
            total = max(len(source_frames), 1)

            for index, frame in enumerate(source_frames):
                if self._stop_if_requested(job_id):
                    return
                completed_ratio = index / total
                self.update(
                    job_id,
                    state="fetching",
                    progress=10 + round(completed_ratio * 15),
                    message=f"Downloading frame {index + 1} of {len(source_frames)}",
                )
                content = self._download_with_retry(camera_api, frame, request, index)
                if self._stop_if_requested(job_id):
                    return

                self.update(
                    job_id,
                    state="validating",
                    progress=25 + round(completed_ratio * 10),
                    message=f"Validating frame {index + 1} of {len(source_frames)}",
                )
                processor.validate_image(content)
                if self._stop_if_requested(job_id):
                    return

                self.update(
                    job_id,
                    state="processing",
                    progress=35 + round(completed_ratio * 10),
                    message=f"Locating frame {index + 1} of {len(source_frames)}",
                )
                city, country = camera_api.reverse_geocode(
                    frame["latitude"], frame["longitude"]
                )
                if self._stop_if_requested(job_id):
                    return

                self.update(
                    job_id,
                    state="processing",
                    progress=45 + round(completed_ratio * 50),
                    message=f"Classifying frame {index + 1} of {len(source_frames)}",
                )
                classification, created = processor.store_and_classify(
                    content=content,
                    city=city,
                    country=country,
                    latitude=frame["latitude"],
                    longitude=frame["longitude"],
                    source="camera-api",
                    namespace="camera-frames",
                )
                items.append(classification)
                if created:
                    new_count += 1
                else:
                    duplicate_count += 1
                self.update(
                    job_id,
                    state="processing",
                    progress=45 + round(((index + 1) / total) * 50),
                    message=f"Processed frame {index + 1} of {len(source_frames)}",
                    items=list(items),
                    new_count=new_count,
                    duplicate_count=duplicate_count,
                )

            self.update(
                job_id,
                state="ready",
                progress=100,
                message=(
                    f"{len(items)} frame(s) processed — "
                    f"{new_count} new, {duplicate_count} already imported"
                ),
                items=items,
                cursor=next_cursor,
                new_count=new_count,
                duplicate_count=duplicate_count,
            )
        except Exception:
            logger.exception("Camera-frame batch job %s failed", job_id)
            self.update(
                job_id,
                state="error",
                progress=100,
                message="Image processing failed",
                error="The camera-frame batch could not be processed.",
            )
        finally:
            db.close()

    @staticmethod
    def _download_with_retry(
        camera_api: CameraApiService,
        frame: dict,
        request: CameraFrameBatchImportRequest,
        index: int,
    ) -> bytes:
        try:
            return camera_api.download_image(frame["image_url"])
        except requests.HTTPError:
            # The presigned URL is only valid for ~1h and may expire mid-batch.
            # Re-fetch the same page (stable order) once to get fresh URLs.
            refreshed_frames, _ = camera_api.fetch_frame_batch(
                size=request.size,
                cursor=request.cursor,
                created_from=request.created_from,
                created_to=request.created_to,
            )
            if index < len(refreshed_frames):
                return camera_api.download_image(refreshed_frames[index]["image_url"])
            raise


camera_frame_batch_jobs = CameraFrameBatchJobManager()
