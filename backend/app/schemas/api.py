from pydantic import BaseModel, ConfigDict, Field


class ApiError(BaseModel):
    detail: str
    code: str


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None


class LabelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    category_id: int
    category: CategoryRead


class ImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    source: str
    img_url: str = Field(serialization_alias="imgUrl")
    city: str
    country: str
    latitude: float | None = None
    longitude: float | None = None
    status: str


class ClassificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    image_id: int
    label_id: int
    category_id: int
    analysis_run_id: int
    label: str
    category: str
    confidence: float
    status: str
    latitude: float | None = None
    longitude: float | None = None
    img_url: str = Field(serialization_alias="imgUrl")
    city: str
    country: str


class AnalysisRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    name: str
    status: str
    model_version: str


class StatsRead(BaseModel):
    image_count: int
    classification_count: int
    category_count: int
    label_count: int
    analysis_run_count: int
    classifications_by_label: dict[str, int]
    classifications_by_category: dict[str, int]
