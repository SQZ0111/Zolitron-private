from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4

from app.db import SessionLocal
from app.schemas.api import ClassificationRead
from app.schemas.image_processing import MapillaryCityBatchImportRequest
from app.services.image_processing import ImageProcessingService
from app.services.mapillary import MapillaryService


@dataclass
class MapillaryBatchJob:
    job_id: str
    state: str = "queued"
    progress: int = 0
    message: str = "Waiting to start"
    items: list[ClassificationRead] = field(default_factory=list)
    pagination_next: str | None = None
    error: str | None = None
    cancel_requested: bool = False


class MapillaryBatchJobManager:
    """Track local MVP batch jobs so the client can display backend progress."""

    def __init__(self):
        self._jobs: dict[str, MapillaryBatchJob] = {}
        self._lock = Lock()

    def create(self) -> MapillaryBatchJob:
        job = MapillaryBatchJob(job_id=str(uuid4()))
        with self._lock:
            self._jobs[job.job_id] = job
            if len(self._jobs) > 100:
                oldest_job_id = next(iter(self._jobs))
                self._jobs.pop(oldest_job_id, None)
        return job

    def get(self, job_id: str) -> MapillaryBatchJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return MapillaryBatchJob(
                job_id=job.job_id,
                state=job.state,
                progress=job.progress,
                message=job.message,
                items=list(job.items),
                pagination_next=job.pagination_next,
                error=job.error,
                cancel_requested=job.cancel_requested,
            )

    def update(self, job_id: str, **changes) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for name, value in changes.items():
                setattr(job, name, value)

    def cancel(self, job_id: str) -> MapillaryBatchJob | None:
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
        request: MapillaryCityBatchImportRequest,
    ) -> None:
        db = SessionLocal()
        try:
            self.update(
                job_id,
                state="fetching",
                progress=5,
                message="Finding Mapillary sites",
            )
            mapillary = MapillaryService()
            source_images, pagination_next = mapillary.fetch_city_image_batch(
                request.city,
                request.limit,
                request.pagination_next,
            )
            if self._stop_if_requested(job_id):
                return

            processor = ImageProcessingService(db)
            items: list[ClassificationRead] = []
            total = max(len(source_images), 1)

            for index, source_image in enumerate(source_images):
                if self._stop_if_requested(job_id):
                    return
                completed_ratio = index / total
                self.update(
                    job_id,
                    state="fetching",
                    progress=10 + round(completed_ratio * 20),
                    message=f"Downloading image {index + 1} of {len(source_images)}",
                )
                content = mapillary.download_image(source_image["image_url"])
                if self._stop_if_requested(job_id):
                    return

                self.update(
                    job_id,
                    state="validating",
                    progress=30 + round(completed_ratio * 15),
                    message=f"Validating image {index + 1} of {len(source_images)}",
                )
                processor.validate_image(content)
                if self._stop_if_requested(job_id):
                    return

                self.update(
                    job_id,
                    state="processing",
                    progress=45 + round(completed_ratio * 50),
                    message=f"Classifying image {index + 1} of {len(source_images)}",
                )
                classification = processor.store_and_classify(
                    content=content,
                    city=request.city,
                    country=request.country,
                    latitude=source_image["latitude"],
                    longitude=source_image["longitude"],
                    source="mapillary",
                    namespace="mapillary",
                )
                items.append(classification)
                self.update(
                    job_id,
                    state="processing",
                    progress=45 + round(((index + 1) / total) * 50),
                    message=f"Processed image {index + 1} of {len(source_images)}",
                    items=list(items),
                )

            self.update(
                job_id,
                state="ready",
                progress=100,
                message=f"{len(items)} image(s) ready",
                items=items,
                pagination_next=pagination_next,
            )
        except Exception:
            self.update(
                job_id,
                state="error",
                progress=100,
                message="Image processing failed",
                error="The Mapillary batch could not be processed.",
            )
        finally:
            db.close()


mapillary_batch_jobs = MapillaryBatchJobManager()
