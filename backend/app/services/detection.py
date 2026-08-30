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

import os
import time
from collections.abc import Callable
from typing import Any

try:
    from inference_sdk import InferenceHTTPClient
except ImportError:  # Keep the API importable so a missing optional SDK returns 503.
    InferenceHTTPClient = None

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
DEFAULT_API_URL = "https://serverless.roboflow.com"

CONFIDENCE_THRESHOLDS = {
    "garbage": 0.65,
    "litter": 0.60,
}


class RoboflowDetectionError(Exception):
    """Raised when detection fails after retries."""
    pass


class DetectionService:
    """Service for running the Roboflow workflow through the inference SDK."""

    def __init__(
        self,
        client_factory: Callable[..., Any] | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        self.workspace_name = os.getenv("ROBOFLOW_WORKSPACE", "yoav1s-workspace")
        self.workflow_id = os.getenv("ROBOFLOW_WORKFLOW_ID", "trash-vtrash-t8mku-2-rfdetr-large-t1-logic-2")
        self.api_url = os.getenv("ROBOFLOW_API_URL", DEFAULT_API_URL)
        self._client_factory = client_factory or InferenceHTTPClient
        self._sleep = sleep

        if not self.api_key:
            raise RoboflowDetectionError(
                "ROBOFLOW_API_KEY environment variable is not set. "
                "Get a key at https://app.roboflow.com/settings/api"
            )
        if self._client_factory is None:
            raise RoboflowDetectionError(
                "inference-sdk is not installed. Install the backend requirements "
                "with Python 3.11 or 3.12."
            )

        self.client = self._client_factory(
            api_url=self.api_url,
            api_key=self.api_key,
        )

    def detect_trash(self, image_path_or_url: str) -> dict:
        """
        Run the trash-detection workflow on a single image.

        Args:
            image_path_or_url: local file path or https:// URL

        Returns:
            dict: workflow output (e.g. {"predictions": {...}})

        Raises:
            RoboflowDetectionError: if the API call fails after retries
        """
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = self.client.run_workflow(
                    workspace_name=self.workspace_name,
                    workflow_id=self.workflow_id,
                    images={"image": image_path_or_url},
                    parameters={},
                )
                if not isinstance(result, list) or not result:
                    raise ValueError("Workflow returned no result for the input image")
                if not isinstance(result[0], dict):
                    raise ValueError("Workflow returned an unexpected response format")
                return result[0]
            except Exception as exc:
                last_error = exc
                if attempt < MAX_RETRIES:
                    self._sleep(RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1)))

        raise RoboflowDetectionError(
            f"Workflow call failed after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error

    def count_detections(self, output: dict) -> dict:
        """
        Count detections by class that meet confidence thresholds.

        Args:
            output: workflow output dict

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

    def extract_predictions(self, output: dict) -> list[dict]:
        """
        Extract predictions with confidence >= threshold.

        Returns list of dicts with class, confidence, x, y, width, height.
        """
        predictions = []
        detections = output.get("predictions", {}).get("predictions", [])

        for detection in detections:
            class_name = detection.get("class")
            confidence = detection.get("confidence", 0)
            threshold = CONFIDENCE_THRESHOLDS.get(class_name)

            if threshold is None or confidence < threshold:
                continue

            predictions.append({
                "class": class_name,
                "confidence": float(confidence),
                "x": detection.get("x"),
                "y": detection.get("y"),
                "width": detection.get("width"),
                "height": detection.get("height"),
            })

        return predictions
