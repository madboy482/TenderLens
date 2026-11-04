from pydantic import BaseModel

from app.llm.base import LLMProviderError
from app.llm.structured_output import StructuredRequirement
from app.nlp.requirement_extraction import extract_requirement


class MockProvider:
    """Free, deterministic provider used for local development and tests."""

    provider_name = "mock"

    def generate_structured(
        self,
        *,
        source_text: str,
        source_chunk_id: str,
        output_model: type[BaseModel],
    ) -> BaseModel:
        extracted = extract_requirement(source_text)
        if extracted is None:
            raise LLMProviderError("The supplied source chunk is not a candidate requirement.")
        result = output_model.model_validate(
            {
                "source_chunk_id": source_chunk_id,
                **extracted.__dict__,
            }
        )
        if isinstance(result, StructuredRequirement):
            result.validate_category()
        return result
