from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel


class LLMProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    provider_name: str

    def generate_structured(
        self,
        *,
        source_text: str,
        source_chunk_id: str,
        output_model: type[BaseModel],
    ) -> BaseModel:
        """Return validated output grounded in the supplied source chunk."""


class SourceBoundInput(BaseModel):
    source_chunk_id: str
    source_text: str


def ensure_source_reference(source_chunk_id: str, allowed_chunk_ids: Sequence[str]) -> None:
    if source_chunk_id not in allowed_chunk_ids:
        raise LLMProviderError("Provider output referenced a chunk outside the supplied input.")
