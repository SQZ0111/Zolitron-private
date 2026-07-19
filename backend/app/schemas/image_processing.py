from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.api import ClassificationRead


class MapillaryCityImportRequest(BaseModel):
    city: str
    country: str = "Germany"
    limit: int = Field(default=5, ge=1, le=25)

    @field_validator("city")
    @classmethod
    def city_must_not_be_empty(cls, city: str) -> str:
        if not city.strip():
            raise ValueError("City must not be empty.")
        return city.strip()


class MapillaryCityBatchImportRequest(MapillaryCityImportRequest):
    model_config = ConfigDict(populate_by_name=True)

    pagination_next: str | None = Field(default=None, alias="paginationNext")


class MapillaryCityBatchImportResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ClassificationRead]
    pagination_next: str | None = Field(serialization_alias="paginationNext")


class MapillaryBatchJobStartResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(serialization_alias="jobId")


class MapillaryBatchJobStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(serialization_alias="jobId")
    state: str
    progress: int
    message: str
    items: list[ClassificationRead] = Field(default_factory=list)
    pagination_next: str | None = Field(
        default=None,
        serialization_alias="paginationNext",
    )
    error: str | None = None
