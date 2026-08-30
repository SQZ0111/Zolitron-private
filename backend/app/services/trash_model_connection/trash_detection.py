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

"""
Standalone trash detection script using Roboflow.

Usage:
    py -3.11 trash_detection.py "path/to/image.jpg"
    py -3.11 trash_detection.py "https://example.com/image.jpg"

Output:
    Prints garbage/litter counts and writes annotated image to image_result/
    (garbage boxes = green, litter boxes = red)

Environment variables required:
    ROBOFLOW_API_KEY - from https://app.roboflow.com/settings/api
    ROBOFLOW_WORKSPACE - workspace name (default: yoav1s-workspace)
    ROBOFLOW_WORKFLOW_ID - workflow ID (default: trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2)
"""

import io
import os
import sys
import time
from urllib.parse import urlparse

import requests
from PIL import Image, ImageDraw, ImageFont
from roboflow import Roboflow

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

CONFIDENCE_THRESHOLDS = {
    "garbage": 0.65,
    "litter": 0.60,
}

BOX_COLORS = {
    "garbage": (0, 200, 0),
    "litter": (220, 0, 0),
}

OUTPUT_DIR = "image_result"
BOX_WIDTH = 4


class TrashDetectionError(Exception):
    """Raised when the workflow call fails after all retries."""


def detect_trash(image_path_or_url: str) -> dict:
    """
    Run the trash-detection workflow on a single image.

    Args:
        image_path_or_url: local file path or https:// URL

    Returns:
        dict: workflow output
    """
    api_key = os.getenv("ROBOFLOW_API_KEY")
    workspace_name = os.getenv("ROBOFLOW_WORKSPACE", "yoav1s-workspace")
    workflow_id = os.getenv("ROBOFLOW_WORKFLOW_ID", "trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2")

    if not api_key:
        raise TrashDetectionError(
            "ROBOFLOW_API_KEY environment variable is not set. "
            "Get a key at https://app.roboflow.com/settings/api"
        )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            rf = Roboflow(api_key=api_key)
            project = rf.workspace(workspace_name).project(workflow_id)
            prediction = project.predict(image_path_or_url, confidence=40)
            return prediction.json() if hasattr(prediction, 'json') else prediction
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1)))

    raise TrashDetectionError(
        f"Workflow call failed after {MAX_RETRIES} attempts: {last_error}"
    ) from last_error


def count_detections(output: dict) -> dict:
    """
    Count detections by class.

    Returns:
        dict: e.g. {"garbage": 2, "litter": 1}
    """
    counts = {class_name: 0 for class_name in CONFIDENCE_THRESHOLDS}

    detections = output.get("predictions", {}).get("predictions", [])
    for detection in detections:
        class_name = detection.get("class")
        confidence = detection.get("confidence", 0)
        threshold = CONFIDENCE_THRESHOLDS.get(class_name)
        if threshold is not None and confidence >= threshold:
            counts[class_name] += 1

    return counts


def _load_image(image_path_or_url: str) -> Image.Image:
    """Load the source image, whether it's a local path or an https:// URL."""
    parsed = urlparse(image_path_or_url)
    if parsed.scheme in ("http", "https"):
        response = requests.get(image_path_or_url, timeout=30)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    return Image.open(image_path_or_url).convert("RGB")


def _output_filename(image_path_or_url: str) -> str:
    """Derive '<name>_result.jpg' from a local path or URL."""
    parsed = urlparse(image_path_or_url)
    base = os.path.basename(parsed.path if parsed.scheme else image_path_or_url)
    stem, _ext = os.path.splitext(base)
    stem = stem or "image"
    return f"{stem}_result.jpg"


def draw_and_save(image_path_or_url: str, output: dict) -> str:
    """
    Draw bounding boxes for detections and save to image_result/.

    Returns:
        str: path of the saved file
    """
    image = _load_image(image_path_or_url)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()

    detections = output.get("predictions", {}).get("predictions", [])
    for detection in detections:
        class_name = detection.get("class")
        confidence = detection.get("confidence", 0)
        threshold = CONFIDENCE_THRESHOLDS.get(class_name)
        if threshold is None or confidence < threshold:
            continue

        color = BOX_COLORS.get(class_name, (255, 255, 0))

        cx, cy = detection.get("x"), detection.get("y")
        w, h = detection.get("width"), detection.get("height")
        if None in (cx, cy, w, h):
            continue

        left = cx - w / 2
        top = cy - h / 2
        right = cx + w / 2
        bottom = cy + h / 2

        draw.rectangle([left, top, right, bottom], outline=color, width=BOX_WIDTH)

        label = f"{class_name} {confidence:.2f}"
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        label_top = max(top - text_h - 4, 0)
        draw.rectangle(
            [left, label_top, left + text_w + 6, label_top + text_h + 4],
            fill=color,
        )
        draw.text((left + 3, label_top + 2), label, fill=(255, 255, 255), font=font)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, _output_filename(image_path_or_url))
    image.save(out_path, "JPEG", quality=95)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python trash_detection.py <image_path_or_url>")
        sys.exit(1)

    try:
        output = detect_trash(sys.argv[1])
    except TrashDetectionError as e:
        print(f"Error: {e}")
        sys.exit(1)

    counts = count_detections(output)
    print(f"Garbage: {counts['garbage']}")
    print(f"Litter: {counts['litter']}")

    saved_path = draw_and_save(sys.argv[1], output)
    print(f"Annotated image saved to: {saved_path}")
