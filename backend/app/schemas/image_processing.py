from pydantic import BaseModel, ConfigDict, Field

from app.schemas.api import ClassificationRead


class CameraFrameBatchImportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int = Field(default=5, ge=1, le=25)
    cursor: str | None = Field(default=None)
    created_from: str | None = Field(default=None, alias="createdFrom")
    created_to: str | None = Field(default=None, alias="createdTo")


class CameraFrameBatchJobStartResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(serialization_alias="jobId")


class CameraFrameBatchJobStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(serialization_alias="jobId")
    state: str
    progress: int
    message: str
    items: list[ClassificationRead] = Field(default_factory=list)
    cursor: str | None = Field(default=None)
    new_count: int = Field(default=0, serialization_alias="newCount")
    duplicate_count: int = Field(default=0, serialization_alias="duplicateCount")
    error: str | None = None
