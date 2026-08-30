# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zolitron
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io

from PIL import Image as PillowImage

from app.db import SessionLocal
from app.services.image_processing import ImageProcessingService
from app.services.image_storage import LocalImageStorage

FRAME_WIDTH = 1000
FRAME_HEIGHT = 1000
# GROUND_REGION_TOP is 0.40, so the ground region is y >= 400 over the full
# width: 1000 * 600 = 600000 px of actionable area in this fabricated frame.
GROUND_LINE = 400
GROUND_AREA = FRAME_WIDTH * (FRAME_HEIGHT - GROUND_LINE)


def _detection(class_name, confidence, *, width=100, height=100, x=500, y=700):
    """One detector box: centre coordinates plus size, in frame pixels."""
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


def test_a_real_garbage_pile_recommends_collection():
    # 300 x 300 fully below the horizon line: 90000 / 600000 = 15% of ground.
    summary = _summarize(_detection("garbage", 0.9, width=300, height=300, y=700))

    assert summary.disposition == "collect"
    assert summary.label == "garbage"
    assert summary.status == "classified"
    assert summary.garbage_count == 1
    assert summary.litter_count == 0
    assert summary.garbage_coverage == 90000 / GROUND_AREA
    assert summary.litter_coverage == 0.0


def test_a_speck_below_the_noise_floor_is_dropped():
    # 50 x 50 is 2500 / 600000 = 0.42% of ground, under MIN_DETECTION_COVERAGE.
    summary = _summarize(_detection("garbage", 0.78, width=50, height=50, y=700))

    assert summary.disposition == "not-garbage"
    assert summary.status == "classified"
    assert summary.label == "garbage"
    assert summary.confidence == 0.78
    assert summary.detections == []
    assert summary.bbox is None
    assert summary.garbage_count == 0
    assert summary.garbage_coverage == 0.0


def test_a_lone_small_garbage_box_is_only_watched():
    # 80 x 80 is 6400 / 600000 = 1.07%: over the noise floor, under 2%.
    summary = _summarize(_detection("garbage", 0.8, width=80, height=80, y=700))

    assert summary.disposition == "watch"
    assert summary.garbage_count == 1
    assert summary.garbage_coverage == 6400 / GROUND_AREA


def test_two_small_garbage_boxes_corroborate_into_a_collection():
    # 70 x 60 each is 4200 / 600000 = 0.7%; the pair sums to 1.4%, still under
    # GARBAGE_COLLECT_COVERAGE, so only GARBAGE_COLLECT_COUNT can escalate it.
    summary = _summarize(
        _detection("garbage", 0.8, width=70, height=60, x=300, y=700),
        _detection("garbage", 0.7, width=70, height=60, x=700, y=800),
    )

    assert summary.disposition == "collect"
    assert summary.garbage_count == 2
    assert summary.garbage_coverage == 8400 / GROUND_AREA
    assert summary.garbage_coverage < 0.02


def test_the_garbage_branch_decides_even_when_litter_is_present():
    summary = _summarize(
        _detection("garbage", 0.66, width=80, height=80, x=300, y=700),
        _detection("litter", 0.99, width=80, height=80, x=700, y=700),
    )

    assert summary.disposition == "watch"
    assert summary.label == "litter"
    assert summary.garbage_count == 1
    assert summary.litter_count == 1


def test_a_box_entirely_above_the_horizon_clips_to_zero():
    # 300 x 300 centred at y = 150 sits wholly in the sky region.
    summary = _summarize(_detection("garbage", 0.9, width=300, height=300, y=150))

    assert summary.disposition == "not-garbage"
    assert summary.garbage_count == 0
    assert summary.garbage_coverage == 0.0
    assert summary.detections == []


def test_a_box_straddling_the_horizon_only_counts_its_lower_half():
    # Centred on the horizon line: 250..550 vertically, so 400..550 counts.
    summary = _summarize(
        _detection("garbage", 0.9, width=300, height=300, y=GROUND_LINE)
    )

    assert summary.garbage_coverage == (300 * 150) / GROUND_AREA
    assert summary.garbage_coverage == 0.075


def test_litter_covering_enough_ground_is_escalated_to_collection():
    # 200 x 180 is 36000 / 600000 = 6% of ground, over LITTER_COLLECT_COVERAGE.
    summary = _summarize(_detection("litter", 0.7, width=200, height=180, y=700))

    assert summary.disposition == "collect"
    assert summary.litter_count == 1
    assert summary.litter_coverage == 0.06


def test_scattered_small_litter_is_only_watched():
    # Three 100 x 40 boxes: 0.67% each, 2% together, under both litter rules.
    summary = _summarize(
        _detection("litter", 0.8, width=100, height=40, x=200, y=600),
        _detection("litter", 0.75, width=100, height=40, x=500, y=700),
        _detection("litter", 0.7, width=100, height=40, x=800, y=800),
    )

    assert summary.disposition == "watch"
    assert summary.litter_count == 3
    assert summary.litter_coverage == 12000 / GROUND_AREA
    assert summary.litter_coverage < 0.05


def test_enough_litter_detections_are_escalated_to_collection():
    summary = _summarize(
        *[_detection("litter", 0.7, width=100, height=40, y=700)] * 6
    )

    assert summary.disposition == "collect"
    assert summary.litter_count == 6
    assert summary.litter_coverage < 0.05


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


def test_coverage_is_clamped_to_the_whole_ground_region():
    summary = _summarize(
        _detection("garbage", 0.9, width=FRAME_WIDTH, height=600, y=700),
        _detection("garbage", 0.8, width=FRAME_WIDTH, height=600, y=700),
    )

    assert summary.garbage_coverage == 1.0


def test_only_surviving_detections_are_kept():
    summary = _summarize(
        _detection("garbage", 0.9, width=300, height=300, x=300, y=700),
        _detection("litter", 0.7, width=200, height=180, x=700, y=700),
        _detection("litter", 0.1, width=200, height=180, x=700, y=200),
        _detection("litter", 0.99, width=40, height=40, x=900, y=900),
    )

    assert len(summary.detections) == 2
    assert [item["class"] for item in summary.detections] == ["garbage", "litter"]
    # The 0.99 box is noise, so the top box is the surviving garbage pile.
    assert summary.label == "garbage"
    assert summary.bbox == {"x": 300, "y": 700, "width": 300, "height": 300}


def test_missing_frame_dimensions_fall_back_to_zero_coverage():
    summary = ImageProcessingService._summarize_output(
        _output(_detection("garbage", 0.9, width=300, height=300, y=700)), None, None
    )

    assert summary.garbage_coverage == 0.0
    assert summary.disposition == "not-garbage"


def test_store_and_classify_persists_disposition_and_surviving_boxes(client, tmp_path):
    db = SessionLocal()
    try:
        service = ImageProcessingService(
            db,
            detector=FakeDetector(
                _output(
                    _detection("litter", 0.9, width=400, height=400, x=200, y=700),
                    _detection("litter", 0.7, width=100, height=100, x=800, y=800),
                    _detection("litter", 0.99, width=40, height=40, x=600, y=900),
                )
            ),
            storage=LocalImageStorage(static_root=tmp_path),
        )
        result, created = service.store_and_classify(
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

    assert created is True
    assert result.label == "litter"
    assert result.disposition == "collect"
    assert result.litter_count == 2
    assert result.garbage_count == 0
    assert len(result.detections) == 2
    assert result.detections[0].class_name == "litter"
    assert result.image_width == FRAME_WIDTH
    assert result.image_height == FRAME_HEIGHT


def test_store_and_classify_reports_known_content_as_not_created(client, tmp_path):
    """The same bytes twice: the second call is a duplicate, and says so."""
    db = SessionLocal()
    try:
        service = ImageProcessingService(
            db,
            detector=FakeDetector(
                _output(_detection("litter", 0.9, width=400, height=400, x=200, y=700))
            ),
            storage=LocalImageStorage(static_root=tmp_path),
        )
        content = _png_bytes(color=(9, 9, 9))
        arguments = dict(
            city="Bochum",
            country="Germany",
            latitude=51.48,
            longitude=7.22,
            source="camera-api",
            namespace="camera-frames",
        )
        first, first_created = service.store_and_classify(content=content, **arguments)
        second, second_created = service.store_and_classify(content=content, **arguments)
    finally:
        db.close()

    assert first_created is True
    assert second_created is False
    assert second.id == first.id
