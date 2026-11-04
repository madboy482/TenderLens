import json
from dataclasses import asdict, dataclass

from app.nlp.retrieval import score_match
from app.nlp.rules_engine import evaluate_evidence


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    requirement: str
    evidence: str
    required_amount: float | None
    expected_retrieval: bool
    expected_rule_status: str


CASES = (
    EvaluationCase(
        "gst_certificate_match",
        "The bidder must submit a valid GST certificate.",
        "GST certificate number GST-123 is valid.",
        None,
        True,
        "evidence_found",
    ),
    EvaluationCase(
        "turnover_threshold_pass",
        "The bidder must have turnover of INR 5 lakh.",
        "Audited turnover certificate confirms INR 7 lakh turnover.",
        500000,
        True,
        "evidence_found",
    ),
    EvaluationCase(
        "turnover_threshold_shortfall",
        "The bidder must have turnover of INR 10 lakh.",
        "Audited turnover certificate confirms INR 7 lakh turnover.",
        1000000,
        True,
        "needs_review",
    ),
    EvaluationCase(
        "unrelated_document",
        "The bidder must submit a valid GST certificate.",
        "The office lease agreement is valid until 31/12/2027.",
        None,
        False,
        "evidence_found",
    ),
    EvaluationCase(
        "expired_certificate",
        "The bidder must submit a valid quality certificate.",
        "Quality certificate expires on 01/01/2020.",
        None,
        False,
        "needs_review",
    ),
    EvaluationCase(
        "ambiguous_amount",
        "The bidder must have turnover of INR 5 lakh.",
        "The financial document mentions turnover but no amount.",
        500000,
        False,
        "needs_review",
    ),
)


def evaluate_cases() -> dict[str, object]:
    retrieval_results = []
    rule_results = []
    for case in CASES:
        retrieval = score_match(case.requirement, case.evidence)
        rule = evaluate_evidence(
            case.requirement,
            case.evidence,
            required_amount=case.required_amount,
        )
        retrieval_results.append((retrieval.score >= 0.5) == case.expected_retrieval)
        rule_results.append(rule.status == case.expected_rule_status)

    def accuracy(results: list[bool]) -> float:
        return round(sum(results) / len(results), 3)

    return {
        "case_count": len(CASES),
        "retrieval_accuracy": accuracy(retrieval_results),
        "rule_accuracy": accuracy(rule_results),
        "cases": [
            {
                **asdict(case),
                "retrieval_score": score_match(case.requirement, case.evidence).score,
                "rule_status": evaluate_evidence(
                    case.requirement,
                    case.evidence,
                    required_amount=case.required_amount,
                ).status,
            }
            for case in CASES
        ],
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_cases(), indent=2))
