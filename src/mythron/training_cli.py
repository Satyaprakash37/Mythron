"""MYTHRON Phase 10 — Training evaluation workflow."""

from pathlib import Path

from mythron.training import (
    evaluate_training_examples,
    load_training_jsonl,
)


def run_training_evaluation(reasoner, dataset_path: str | Path) -> dict:
    """Load a controlled training dataset and evaluate it with a reasoner."""

    examples = load_training_jsonl(str(dataset_path))
    result = evaluate_training_examples(reasoner, examples)

    return {
        "passed": result.passed,
        "summary": result.summary,
        "failed_cases": result.failed_cases,
        "case_statuses": result.case_statuses,
    }


def main(argv=None) -> int:
    """Run controlled training evaluation from the command line."""

    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Run MYTHRON controlled training evaluation."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to the training JSONL dataset.",
    )
    parser.add_argument(
        "--mock-response",
        required=True,
        help="Deterministic response used for local CLI testing.",
    )

    args = parser.parse_args(argv)

    class MockReasoner:
        def reason(self, prompt):
            return args.mock_response

    report = run_training_evaluation(
        MockReasoner(),
        args.dataset,
    )

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
