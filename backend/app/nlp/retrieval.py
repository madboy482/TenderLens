import re
from dataclasses import dataclass


_STOP_WORDS = {
    "a", "an", "and", "be", "for", "have", "in", "is", "of", "on", "or",
    "submit", "the", "to", "with",
}


def _terms(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", text.lower())
        if len(term) > 2 and term not in _STOP_WORDS
    }


@dataclass(frozen=True)
class RetrievalResult:
    score: float
    matched_terms: tuple[str, ...]


def score_match(query: str, candidate: str) -> RetrievalResult:
    query_terms = _terms(query)
    candidate_terms = _terms(candidate)
    if not query_terms or not candidate_terms:
        return RetrievalResult(0.0, ())
    matched = sorted(query_terms & candidate_terms)
    return RetrievalResult(len(matched) / len(query_terms), tuple(matched))
