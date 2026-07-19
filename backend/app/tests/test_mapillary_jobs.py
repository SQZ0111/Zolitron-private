from app.services.mapillary_jobs import MapillaryBatchJobManager


def test_batch_job_can_be_marked_for_cancellation():
    manager = MapillaryBatchJobManager()
    job = manager.create()

    cancelled = manager.cancel(job.job_id)

    assert cancelled is not None
    assert cancelled.state == "stopping"
    assert cancelled.cancel_requested is True
