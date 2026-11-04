import re
from dataclasses import dataclass

from app.nlp.clause_candidates import is_candidate_clause

CATEGORIES = (
    "eligibility",
    "financial",
    "technical",
    "document/certificate",
    "deadline",
    "delivery/performance",
    "commercial",
    "other",
)


@dataclass(frozen=True)
class ExtractedRequirement:
    normalized_text: str
    category: str
    requirement_type: str
    mandatory_status: str
    extracted_value: str | None
    normalized_value: str | None
    unit: str | None
    conditions: str | None
    confidence: float


def _category(text: str) -> str:
    value = text.lower()
    if any(term in value for term in ("turnover", "net worth", "financial", "emd", "amount")):
        return "financial"
    if any(term in value for term in ("certificate", "gst", "pan", "registration", "document")):
        return "document/certificate"
    if any(term in value for term in ("deadline", "due date", "within", "submission date", "validity")):
        return "deadline"
    if any(term in value for term in ("delivery", "performance security", "warranty")):
        return "delivery/performance"
    if any(term in value for term in ("technical", "specification", "capacity")):
        return "technical"
    if any(term in value for term in ("eligible", "eligibility", "qualification", "experience")):
        return "eligibility"
    return "other"


def _amount(text: str) -> tuple[str | None, str | None, str | None]:
    match = re.search(
        r"(?:inr|rs\.?|₹)\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|crore|crores)?",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None, None, None
    raw_number = match.group(1).replace(",", "")
    scale = (match.group(2) or "").lower() or None
    try:
        number = float(raw_number)
        multiplier = 100000 if scale in ("lakh", "lakhs") else 10000000 if scale in ("crore", "crores") else 1
        normalized = str(int(number * multiplier)) if number.is_integer() else str(number * multiplier)
    except ValueError:
        normalized = None
    return match.group(0), normalized, "INR"


def extract_requirement(text: str) -> ExtractedRequirement | None:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned or not is_candidate_clause(cleaned):
        return None
    lower = cleaned.lower()
    mandatory = "mandatory" if "mandatory" in lower else "unknown"
    if any(term in lower for term in ("shall", "must", "required", "bidder should")):
        mandatory = "mandatory"
    elif any(term in lower for term in ("if applicable", "where applicable", "may")):
        mandatory = "conditional"
    extracted_value, normalized_value, unit = _amount(cleaned)
    category = _category(cleaned)
    requirement_type = "financial" if category == "financial" else "documentary"
    return ExtractedRequirement(
        normalized_text=cleaned,
        category=category,
        requirement_type=requirement_type,
        mandatory_status=mandatory,
        extracted_value=extracted_value,
        normalized_value=normalized_value,
        unit=unit,
        conditions=None,
        confidence=0.75 if mandatory != "unknown" else 0.55,
    )
