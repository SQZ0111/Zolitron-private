from pydantic import BaseModel, Field


class DetectionPredictionRead(BaseModel):
    """Single prediction from the detection model."""
    class_name: str = Field(alias="class")
    confidence: float
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None


class ClassifyImageRequest(BaseModel):
    """Request to classify an image."""
    image_url: str
    city: str | None = None
    country: str = "Germany"


class ClassifyImageResponse(BaseModel):
    """Response from image classification."""
    predictions: list[DetectionPredictionRead]
    garbage_count: int
    litter_count: int
    total_detections: int
