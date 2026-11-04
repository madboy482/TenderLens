import re
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class RuleResult:
    status: str
    reason: str


def parse_date(text: str) -> date | None:
    for pattern in (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", r"\b(\d{4})-(\d{2})-(\d{2})\b"):
        match = re.search(pattern, text)
        if not match:
            continue
        try:
            if pattern.startswith(r"\b(\d{4})"):
                return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        except ValueError:
            return None
    return None


def parse_inr_amount(text: str) -> float | None:
    match = re.search(
        r"(?:inr|rs\.?|₹)\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|crore|crores)?",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    try:
        value = float(match.group(1).replace(",", ""))
    except ValueError:
        return None
    scale = (match.group(2) or "").lower()
    return value * (100000 if scale in ("lakh", "lakhs") else 10000000 if scale in ("crore", "crores") else 1)


def evaluate_evidence(
    requirement_text: str,
    evidence_text: str,
    *,
    required_amount: float | None = None,
    today: date | None = None,
) -> RuleResult:
    """Apply only clear rules; ambiguous results remain needs_review."""
    current_date = today or date.today()
    evidence_date = parse_date(evidence_text)
    if evidence_date is not None and any(term in evidence_text.lower() for term in ("expiry", "expires", "valid until", "validity")):
        if evidence_date < current_date:
            return RuleResult("needs_review", f"Evidence date {evidence_date.isoformat()} is expired.")
        return RuleResult("evidence_found", f"Evidence date {evidence_date.isoformat()} is not expired.")

    if required_amount is not None:
        evidence_amount = parse_inr_amount(evidence_text)
        if evidence_amount is None:
            return RuleResult("needs_review", "Evidence amount or currency could not be extracted confidently.")
        if evidence_amount >= required_amount:
            return RuleResult("evidence_found", "Evidence amount meets the extracted threshold.")
        return RuleResult("needs_review", "Evidence amount is below the extracted threshold.")

    return RuleResult("evidence_found", "A candidate evidence snippet was found; human confirmation is required.")
