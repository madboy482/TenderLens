from dataclasses import dataclass

from app.nlp.retrieval import score_match


@dataclass(frozen=True)
class ClauseChange:
    change_type: str
    old_text: str | None
    new_text: str | None
    old_page: int | None
    new_page: int | None
    similarity: float


def compare_clauses(
    original: list[tuple[int, str]], amendment: list[tuple[int, str]]
) -> list[ClauseChange]:
    """Compare bounded clauses without overwriting either source document."""
    changes: list[ClauseChange] = []
    used_amendment: set[int] = set()
    for old_page, old_text in original:
        best_index = None
        best_score = 0.0
        for index, (new_page, new_text) in enumerate(amendment):
            if index in used_amendment:
                continue
            score = score_match(old_text, new_text).score
            if score > best_score:
                best_index, best_score = index, score
        if best_index is None or best_score < 0.25:
            changes.append(ClauseChange("possibly_removed", old_text, None, old_page, None, best_score))
            continue
        used_amendment.add(best_index)
        new_page, new_text = amendment[best_index]
        change_type = "unchanged" if old_text.strip().lower() == new_text.strip().lower() else "changed"
        changes.append(ClauseChange(change_type, old_text, new_text, old_page, new_page, best_score))
    for index, (new_page, new_text) in enumerate(amendment):
        if index not in used_amendment:
            changes.append(ClauseChange("added", None, new_text, None, new_page, 0.0))
    return changes
