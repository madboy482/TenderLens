import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceChunk:
    page_start: int
    page_end: int
    text: str


def split_page_text(
    page_number: int, text: str, max_chars: int = 1200
) -> list[SourceChunk]:
    """Split a page into bounded chunks without losing its page reference."""
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", normalized) if part.strip()]
    chunks: list[SourceChunk] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(SourceChunk(page_number, page_number, current))
                current = ""
            for start in range(0, len(paragraph), max_chars):
                chunks.append(
                    SourceChunk(page_number, page_number, paragraph[start : start + max_chars])
                )
            continue
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if current and len(candidate) > max_chars:
            chunks.append(SourceChunk(page_number, page_number, current))
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(SourceChunk(page_number, page_number, current))
    return chunks
