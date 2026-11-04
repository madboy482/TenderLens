import pytest

from app.core.config import Settings
from app.llm.base import LLMProviderError, ensure_source_reference
from app.llm.factory import create_provider
from app.llm.structured_output import StructuredRequirement


def test_mock_provider_returns_schema_validated_source_bound_output() -> None:
    provider = create_provider(Settings(llm_provider="mock"))

    result = provider.generate_structured(
        source_text="The bidder must submit a valid GST certificate.",
        source_chunk_id="chunk-1",
        output_model=StructuredRequirement,
    )

    assert isinstance(result, StructuredRequirement)
    assert result.source_chunk_id == "chunk-1"
    assert result.category == "document/certificate"


def test_provider_rejects_unsupported_configuration() -> None:
    with pytest.raises(LLMProviderError, match="Unsupported LLM provider"):
        create_provider(Settings(llm_provider="paid-api"))


def test_source_reference_guard_rejects_untrusted_chunk_id() -> None:
    with pytest.raises(LLMProviderError, match="outside"):
        ensure_source_reference("invented", ["chunk-1"])
