import re

from app.nlp.chunking import SourceChunk

_CANDIDATE_CUES = (
    "eligibility",
    "qualification",
    "turnover",
    "net worth",
    "experience",
    "emd",
    "earnest money",
    "performance security",
    "certificate",
    "gst",
    "pan",
    "technical specification",
    "delivery",
    "validity",
    "deadline",
    "corrigendum",
    "amendment",
    "shall",
    "must",
    "required",
)


def is_candidate_clause(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).lower()
    return any(cue in normalized for cue in _CANDIDATE_CUES)


def find_candidate_clauses(chunks: list[SourceChunk]) -> list[SourceChunk]:
    return [chunk for chunk in chunks if is_candidate_clause(chunk.text)]
