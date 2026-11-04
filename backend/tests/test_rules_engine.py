from datetime import date

from app.nlp.rules_engine import evaluate_evidence, parse_date, parse_inr_amount


def test_parses_dates_and_inr_amounts() -> None:
    assert parse_date("Valid until 31/12/2030") == date(2030, 12, 31)
    assert parse_inr_amount("Turnover: INR 5 lakh") == 500000


def test_threshold_rule_handles_pass_and_fail() -> None:
    passed = evaluate_evidence(
        "Turnover must be INR 5 lakh",
        "Annual turnover INR 7 lakh",
        required_amount=500000,
        today=date(2026, 1, 1),
    )
    failed = evaluate_evidence(
        "Turnover must be INR 5 lakh",
        "Annual turnover INR 2 lakh",
        required_amount=500000,
        today=date(2026, 1, 1),
    )
    assert passed.status == "evidence_found"
    assert failed.status == "needs_review"


def test_expired_evidence_is_needs_review() -> None:
    result = evaluate_evidence(
        "Certificate required",
        "Certificate valid until 01/01/2025",
        today=date(2026, 1, 1),
    )
    assert result.status == "needs_review"
