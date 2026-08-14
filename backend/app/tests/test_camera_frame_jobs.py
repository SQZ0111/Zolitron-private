from app.services.camera_frame_jobs import CameraFrameBatchJobManager


def test_batch_job_can_be_marked_for_cancellation():
    manager = CameraFrameBatchJobManager()
    job = manager.create()

    cancelled = manager.cancel(job.job_id)

    assert cancelled is not None
    assert cancelled.state == "stopping"
    assert cancelled.cancel_requested is True
