from pydantic import BaseModel, Field, field_validator


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
