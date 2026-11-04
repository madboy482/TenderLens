from pydantic import BaseModel, ConfigDict, Field

from app.nlp.requirement_extraction import CATEGORIES


class StructuredRequirement(BaseModel):
    """Schema boundary for model-suggested requirement extraction."""

    model_config = ConfigDict(extra="forbid")

    source_chunk_id: str
    normalized_text: str = Field(min_length=1)
    category: str = Field(default="other")
    requirement_type: str = Field(default="documentary")
    mandatory_status: str = Field(default="unknown")
    extracted_value: str | None = None
    normalized_value: str | None = None
    unit: str | None = None
    conditions: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)

    def validate_category(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"Unsupported requirement category: {self.category}")
