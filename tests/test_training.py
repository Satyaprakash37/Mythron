from pathlib import Path

import pytest

from mythron.training import TrainingExample, validate_training_example


def test_valid_training_example():
    example = TrainingExample(
        task="Analyze a local assessment observation",
        input="A local web response is missing a security header.",
        expected_output="Record the missing header as a finding.",
        category="http_response_header",
    )

    assert validate_training_example(example) == example


def test_training_example_rejects_empty_field():
    example = TrainingExample(
        task="",
        input="Observation",
        expected_output="Expected result",
        category="http_response_header",
    )

    with pytest.raises(ValueError, match="task"):
        validate_training_example(example)


def test_training_example_rejects_unsafe_scope():
    example = TrainingExample(
        task="Analyze an observation",
        input="Observation",
        expected_output="Expected result",
        category="http_response_header",
        safety="unrestricted",
    )

    with pytest.raises(ValueError, match="authorized_local_only"):
        validate_training_example(example)


def test_load_training_jsonl(tmp_path: Path):
    dataset = tmp_path / "examples.jsonl"
    dataset.write_text(
        '{"task":"Task","input":"Input","expected_output":"Output",'
        '"category":"test","safety":"authorized_local_only"}\n',
        encoding="utf-8",
    )

    from mythron.training import load_training_jsonl

    examples = load_training_jsonl(str(dataset))

    assert len(examples) == 1
    assert examples[0].task == "Task"
    assert examples[0].category == "test"


def test_load_training_jsonl_rejects_invalid_json(tmp_path: Path):
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text("{invalid}\n", encoding="utf-8")

    from mythron.training import load_training_jsonl

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_training_jsonl(str(dataset))


def test_load_training_jsonl_rejects_missing_field(tmp_path: Path):
    dataset = tmp_path / "missing.jsonl"
    dataset.write_text(
        '{"task":"Task","input":"Input","category":"test",'
        '"safety":"authorized_local_only"}\n',
        encoding="utf-8",
    )

    from mythron.training import load_training_jsonl

    with pytest.raises(ValueError, match="expected_output"):
        load_training_jsonl(str(dataset))


def test_build_training_prompt():
    from mythron.training import build_training_prompt

    example = TrainingExample(
        task="Analyze an authorized local observation",
        input="A local web response is missing CSP.",
        expected_output="Record the missing CSP as a finding.",
        category="http_response_header",
    )

    prompt = build_training_prompt(example)

    assert "Analyze an authorized local observation" in prompt
    assert "A local web response is missing CSP." in prompt
    assert "Record the missing CSP as a finding." in prompt
    assert "http_response_header" in prompt
    assert "authorized_local_only" in prompt


def test_run_training_example_with_reasoner():
    from mythron.training import run_training_example

    class FakeReasoner:
        def __init__(self):
            self.prompts = []

        def reason(self, prompt):
            self.prompts.append(prompt)
            return "Training example processed."

    example = TrainingExample(
        task="Analyze an authorized local observation",
        input="A local web response is missing CSP.",
        expected_output="Record the missing CSP as a finding.",
        category="http_response_header",
    )

    reasoner = FakeReasoner()
    result = run_training_example(reasoner, example)

    assert result == "Training example processed."
    assert len(reasoner.prompts) == 1
    assert "missing CSP" in reasoner.prompts[0]
