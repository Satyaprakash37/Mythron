from mythron.evaluation import EvaluationCase


def test_evaluation_case_passes_when_expected_matches_actual():
    case = EvaluationCase(
        name="Local discovery",
        objective="Discover the authorized local target",
        expected="target discovered",
        actual="target discovered",
    )

    assert case.passed is True


def test_evaluation_case_fails_when_expected_does_not_match_actual():
    case = EvaluationCase(
        name="Local discovery",
        objective="Discover the authorized local target",
        expected="target discovered",
        actual="target not discovered",
    )

    assert case.passed is False


def test_evaluation_case_can_store_notes():
    case = EvaluationCase(
        name="Finding analysis",
        objective="Analyze a discovered finding",
        expected="actionable",
        actual="actionable",
        notes="Controlled local assessment",
    )

    assert case.notes == "Controlled local assessment"


def test_evaluation_suite_summarizes_cases():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    suite.add(
        EvaluationCase(
            name="Case 1",
            objective="Check discovery",
            expected="success",
            actual="success",
        )
    )

    suite.add(
        EvaluationCase(
            name="Case 2",
            objective="Check analysis",
            expected="success",
            actual="failure",
        )
    )

    summary = suite.summary()

    assert summary == {
        "total": 2,
        "passed": 1,
        "failed": 1,
    }


def test_evaluation_suite_passes_only_when_all_cases_pass():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    suite.add(
        EvaluationCase(
            name="Case 1",
            objective="Check workflow",
            expected="success",
            actual="success",
        )
    )

    assert suite.passed is True

    suite.add(
        EvaluationCase(
            name="Case 2",
            objective="Check reporting",
            expected="success",
            actual="failure",
        )
    )

    assert suite.passed is False


def test_evaluation_result_exposes_suite_status():
    from mythron.evaluation import EvaluationResult, EvaluationSuite

    suite = EvaluationSuite()
    suite.add(
        EvaluationCase(
            name="Discovery",
            objective="Discover target",
            expected="success",
            actual="success",
        )
    )

    result = EvaluationResult.from_suite(suite)

    assert result.passed is True
    assert result.summary == {
        "total": 1,
        "passed": 1,
        "failed": 0,
    }


def test_evaluation_result_can_identify_failed_cases():
    from mythron.evaluation import EvaluationResult, EvaluationSuite

    suite = EvaluationSuite()
    suite.add(
        EvaluationCase(
            name="Discovery",
            objective="Discover target",
            expected="success",
            actual="failure",
        )
    )

    result = EvaluationResult.from_suite(suite)

    assert result.passed is False
    assert result.failed_cases == ["Discovery"]


def test_evaluation_suite_rejects_duplicate_case_names():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    case = EvaluationCase(
        name="Discovery",
        objective="Discover target",
        expected="success",
        actual="success",
    )

    suite.add(case)

    try:
        suite.add(case)
    except ValueError as exc:
        assert str(exc) == "Evaluation case name already exists."
    else:
        raise AssertionError("Duplicate evaluation case should be rejected.")


def test_evaluation_suite_can_run_cases():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    suite.add(
        EvaluationCase(
            name="Discovery",
            objective="Discover target",
            expected="success",
            actual="success",
        )
    )

    result = suite.run()

    assert result.passed is True
    assert result.summary == {"total": 1, "passed": 1, "failed": 0}


def test_empty_evaluation_suite_returns_passing_result():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    result = suite.run()

    assert result.passed is True
    assert result.summary == {"total": 0, "passed": 0, "failed": 0}
    assert result.failed_cases == []


def test_evaluation_result_exposes_case_statuses():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    suite.add(
        EvaluationCase(
            name="Discovery",
            objective="Discover target",
            expected="success",
            actual="success",
        )
    )

    suite.add(
        EvaluationCase(
            name="Analysis",
            objective="Analyze finding",
            expected="success",
            actual="failure",
        )
    )

    result = suite.run()

    assert result.case_statuses == {
        "Discovery": True,
        "Analysis": False,
    }


def test_evaluation_suite_rejects_duplicate_names_from_different_objects():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    suite.add(
        EvaluationCase(
            name="Discovery",
            objective="First discovery check",
            expected="success",
            actual="success",
        )
    )

    duplicate = EvaluationCase(
        name="Discovery",
        objective="Second discovery check",
        expected="success",
        actual="success",
    )

    try:
        suite.add(duplicate)
    except ValueError as exc:
        assert str(exc) == "Evaluation case name already exists."
    else:
        raise AssertionError("Duplicate evaluation case name should be rejected.")


def test_evaluation_result_keeps_case_statuses_independent():
    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    suite.add(
        EvaluationCase(
            name="Discovery",
            objective="Discover target",
            expected="success",
            actual="success",
        )
    )

    result = suite.run()

    result.case_statuses["Injected"] = False

    assert "Injected" not in suite.all()[0].name
    assert result.case_statuses["Discovery"] is True
