import io

from PIL import Image as PillowImage

from app.db import SessionLocal
from app.services.image_processing import ImageProcessingService
from app.services.image_storage import LocalImageStorage

FRAME_WIDTH = 1000
FRAME_HEIGHT = 1000


def _detection(class_name, confidence, *, width=100, height=100, x=500, y=500):
    return {
        "class": class_name,
        "confidence": confidence,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }


def _output(*detections):
    return {"predictions": {"predictions": list(detections)}}


def _summarize(*detections):
    return ImageProcessingService._summarize_output(
        _output(*detections), FRAME_WIDTH, FRAME_HEIGHT
    )


class FakeDetector:
    """Stands in for DetectionService so tests never call Roboflow."""

    workflow_id = "test-workflow"

    def __init__(self, output):
        self.output = output

    def detect_trash(self, image_path_or_url):
        return self.output


def _png_bytes(width=FRAME_WIDTH, height=FRAME_HEIGHT, color=(20, 40, 60)):
    buffer = io.BytesIO()
    PillowImage.new("RGB", (width, height), color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_any_accepted_garbage_detection_recommends_collection():
    summary = _summarize(_detection("garbage", 0.9, width=100, height=100))

    assert summary.disposition == "collect"
    assert summary.label == "garbage"
    assert summary.status == "classified"
    assert summary.garbage_count == 1
    assert summary.litter_count == 0
    assert summary.garbage_coverage == 0.01
    assert summary.litter_coverage == 0.0


def test_garbage_is_never_downgraded_by_sparse_litter():
    summary = _summarize(
        _detection("garbage", 0.66, width=10, height=10),
        _detection("litter", 0.99, width=10, height=10),
    )

    assert summary.disposition == "collect"
    assert summary.label == "litter"
    assert summary.garbage_count == 1
    assert summary.litter_count == 1


def test_sparse_litter_is_only_watched():
    summary = _summarize(
        _detection("litter", 0.8, width=100, height=100),
        _detection("litter", 0.7, width=100, height=100),
    )

    assert summary.disposition == "watch"
    assert summary.label == "litter"
    assert summary.litter_count == 2
    assert summary.litter_coverage == 0.02


def test_litter_covering_enough_of_the_frame_is_escalated_to_collection():
    summary = _summarize(_detection("litter", 0.7, width=400, height=400))

    assert summary.disposition == "collect"
    assert summary.litter_count == 1
    assert summary.litter_coverage == 0.16


def test_enough_litter_detections_are_escalated_to_collection():
    summary = _summarize(*[_detection("litter", 0.7, width=10, height=10)] * 6)

    assert summary.disposition == "collect"
    assert summary.litter_count == 6
    assert summary.litter_coverage < 0.12


def test_sub_threshold_detections_keep_the_real_class_and_no_disposition():
    summary = _summarize(
        _detection("garbage", 0.5),
        _detection("litter", 0.55),
    )

    assert summary.status == "low-confidence"
    assert summary.label == "litter"
    assert summary.disposition is None
    assert summary.detections == []


def test_output_without_supported_detections_is_not_garbage():
    summary = _summarize(_detection("overgrown", 0.99))

    assert summary.label == "not-garbage"
    assert summary.disposition == "not-garbage"
    assert summary.status == "classified"
    assert summary.confidence == 0.0
    assert summary.bbox is None


def test_coverage_is_clamped_to_the_whole_frame():
    summary = _summarize(
        _detection("garbage", 0.9, width=FRAME_WIDTH, height=FRAME_HEIGHT),
        _detection("garbage", 0.8, width=FRAME_WIDTH, height=FRAME_HEIGHT),
    )

    assert summary.garbage_coverage == 1.0


def test_every_accepted_detection_is_kept():
    summary = _summarize(
        _detection("garbage", 0.9),
        _detection("litter", 0.7),
        _detection("litter", 0.1),
    )

    assert len(summary.detections) == 2
    assert [item["class"] for item in summary.detections] == ["garbage", "litter"]
    assert summary.bbox == {"x": 500, "y": 500, "width": 100, "height": 100}


def test_store_and_classify_persists_disposition_and_all_boxes(client, tmp_path):
    db = SessionLocal()
    try:
        service = ImageProcessingService(
            db,
            detector=FakeDetector(
                _output(
                    _detection("litter", 0.9, width=400, height=400, x=200, y=200),
                    _detection("litter", 0.7, width=100, height=100, x=800, y=800),
                )
            ),
            storage=LocalImageStorage(static_root=tmp_path),
        )
        result = service.store_and_classify(
            content=_png_bytes(),
            city="Bochum",
            country="Germany",
            latitude=51.48,
            longitude=7.22,
            source="upload",
            namespace="uploads",
        )
    finally:
        db.close()

    assert result.label == "litter"
    assert result.disposition == "collect"
    assert result.litter_count == 2
    assert result.garbage_count == 0
    assert len(result.detections) == 2
    assert result.detections[0].class_name == "litter"
    assert result.image_width == FRAME_WIDTH
    assert result.image_height == FRAME_HEIGHT
