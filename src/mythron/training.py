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
