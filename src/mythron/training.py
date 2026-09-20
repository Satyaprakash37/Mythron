"""MYTHRON Phase 10 — Training data models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingExample:
    """Represent one controlled training example."""

    task: str
    input: str
    expected_output: str
    category: str
    safety: str = "authorized_local_only"


def validate_training_example(example: TrainingExample) -> TrainingExample:
    """Validate one controlled training example."""

    required_fields = {
        "task": example.task,
        "input": example.input,
        "expected_output": example.expected_output,
        "category": example.category,
        "safety": example.safety,
    }

    for field_name, value in required_fields.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Training example field '{field_name}' must be a non-empty string."
            )

    if example.safety != "authorized_local_only":
        raise ValueError(
            "Training example safety must be 'authorized_local_only'."
        )

    return example


import json
from pathlib import Path


def load_training_jsonl(path: str) -> list[TrainingExample]:
    """Load and validate controlled training examples from JSONL."""

    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"Could not read training dataset: {exc}") from exc

    required = {"task", "input", "expected_output", "category", "safety"}
    examples: list[TrainingExample] = []

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON on line {line_number}: {exc.msg}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                f"Training example on line {line_number} must be a JSON object."
            )

        missing = required - data.keys()
        if missing:
            fields = ", ".join(sorted(missing))
            raise ValueError(
                f"Missing required field(s) on line {line_number}: {fields}"
            )

        try:
            example = TrainingExample(
                task=data["task"],
                input=data["input"],
                expected_output=data["expected_output"],
                category=data["category"],
                safety=data["safety"],
            )
            examples.append(validate_training_example(example))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid training example on line {line_number}: {exc}"
            ) from exc

    return examples


def build_training_prompt(example: TrainingExample) -> str:
    """Build a structured prompt from one controlled training example."""

    validate_training_example(example)

    return (
        "MYTHRON CONTROLLED TRAINING EXAMPLE\n"
        f"Safety scope: {example.safety}\n"
        f"Category: {example.category}\n\n"
        f"Task:\n{example.task}\n\n"
        f"Input:\n{example.input}\n\n"
        f"Expected output:\n{example.expected_output}\n"
    )


def run_training_example(reasoner, example: TrainingExample) -> str:
    """Run one controlled training example through a reasoning-compatible object."""

    validate_training_example(example)
    prompt = build_training_prompt(example)
    return reasoner.reason(prompt)


def evaluate_training_example(reasoner, example: TrainingExample):
    """Run one controlled example and compare its output with the expected output."""

    from mythron.evaluation import EvaluationCase

    actual = run_training_example(reasoner, example)

    return EvaluationCase(
        name=example.task,
        objective=example.task,
        expected=example.expected_output,
        actual=actual,
        notes=f"Category: {example.category}; Safety: {example.safety}",
    )


def evaluate_training_examples(reasoner, examples):
    """Evaluate multiple controlled training examples as one suite."""

    from mythron.evaluation import EvaluationSuite

    suite = EvaluationSuite()

    for example in examples:
        suite.add(evaluate_training_example(reasoner, example))

    return suite.run()


def training_evaluation_report(reasoner, examples):
    """Return a serializable report for a batch training evaluation."""

    result = evaluate_training_examples(reasoner, examples)

    return {
        "passed": result.passed,
        "summary": result.summary,
        "failed_cases": result.failed_cases,
        "case_statuses": result.case_statuses,
    }
