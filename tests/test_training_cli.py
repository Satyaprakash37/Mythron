from pathlib import Path

from mythron.training import TrainingExample


def test_run_training_evaluation(tmp_path):
    from mythron.training_cli import run_training_evaluation

    dataset = tmp_path / "training.jsonl"
    dataset.write_text(
        '{"task":"Analyze CSP","input":"Missing Content-Security-Policy",'
        '"expected_output":"CSP finding identified.",'
        '"category":"http_response_header",'
        '"safety":"authorized_local_only"}\n',
        encoding="utf-8",
    )

    class FakeReasoner:
        def reason(self, prompt):
            return "CSP finding identified."

    report = run_training_evaluation(
        FakeReasoner(),
        Path(dataset),
    )

    assert report["passed"] is True
    assert report["summary"] == {
        "total": 1,
        "passed": 1,
        "failed": 0,
    }
    assert report["failed_cases"] == []


def test_cli_main_prints_report(tmp_path, capsys):
    from mythron.training_cli import main

    dataset = tmp_path / "training.jsonl"
    dataset.write_text(
        '{"task":"Analyze CSP","input":"Missing Content-Security-Policy",'
        '"expected_output":"CSP finding identified.",'
        '"category":"http_response_header",'
        '"safety":"authorized_local_only"}\n',
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--dataset",
            str(dataset),
            "--mock-response",
            "CSP finding identified.",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"passed": true' in captured.out
    assert '"total": 1' in captured.out
