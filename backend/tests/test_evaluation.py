from app.evaluation import evaluate_cases


def test_evaluation_fixture_measures_expected_baseline() -> None:
    result = evaluate_cases()

    assert result["case_count"] == 6
    assert result["retrieval_accuracy"] >= 0.8
    assert result["rule_accuracy"] == 1.0
