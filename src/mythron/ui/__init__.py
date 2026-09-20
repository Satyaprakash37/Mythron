"""MYTHRON Phase 11 — Desktop UI."""

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QGroupBox,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


def create_app(argv=None) -> QApplication:
    """Create or return the Qt application instance."""

    app = QApplication.instance()

    if app is None:
        app = QApplication(argv or [])

    return app


class MainWindow(QMainWindow):
    """Main MYTHRON desktop window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("MYTHRON")
        self.resize(1100, 700)

        central = QWidget()
        layout = QVBoxLayout(central)

        brand = QLabel("MYTHRON")
        dashboard = QLabel("Dashboard")
        system_status = QLabel("System Status")
        assessment = QLabel("Assessment")
        findings = QLabel("Findings")
        evidence = QLabel("Evidence")
        training_evaluation = QLabel("Training Evaluation")
        self.training_status = QLabel("No training evaluation run yet.")
        self.assessment_status = QLabel("No assessment started.")
        self.assessment_state = QLabel("Ready")

        assessment_panel = QGroupBox("Assessment")
        assessment_layout = QVBoxLayout(assessment_panel)
        assessment_layout.addWidget(assessment)
        assessment_layout.addWidget(self.assessment_status)
        assessment_layout.addWidget(self.assessment_state)

        findings_panel = QGroupBox("Findings")
        findings_layout = QVBoxLayout(findings_panel)
        findings_layout.addWidget(findings)
        self.findings_status = QPlainTextEdit()
        self.findings_status.setReadOnly(True)
        self.findings_status.setPlaceholderText("No findings available.")
        findings_layout.addWidget(self.findings_status)

        evidence_panel = QGroupBox("Evidence")
        evidence_layout = QVBoxLayout(evidence_panel)
        evidence_layout.addWidget(evidence)
        self.evidence_status = QPlainTextEdit()
        self.evidence_status.setReadOnly(True)
        self.evidence_status.setPlaceholderText("No evidence available.")
        evidence_layout.addWidget(self.evidence_status)

        training_panel = QGroupBox("Training Evaluation")
        training_layout = QVBoxLayout(training_panel)
        training_layout.addWidget(training_evaluation)
        training_layout.addWidget(self.training_status)

        layout.addWidget(brand)
        layout.addWidget(dashboard)
        layout.addWidget(system_status)
        layout.addWidget(assessment_panel)
        layout.addWidget(findings_panel)
        layout.addWidget(evidence_panel)
        layout.addWidget(training_panel)

        self.setCentralWidget(central)

    def show_training_report(self, report: dict) -> None:
        """Display a controlled training evaluation summary."""

        summary = report.get("summary", {})
        passed = summary.get("passed", 0)
        total = summary.get("total", 0)

        self.training_status.setText(
            f"{passed} / {total} passed"
        )

    def show_assessment_status(self, status: str) -> None:
        """Display the current authorized assessment status."""

        self.assessment_status.setText(status)

    def set_assessment_state(self, state: str) -> None:
        """Update the assessment lifecycle state."""

        self.assessment_state.setText(state)

    def show_findings(self, findings: list[str]) -> None:
        """Display assessment findings in the read-only findings panel."""

        self.findings_status.setPlainText("\n".join(findings))

    def show_evidence(self, evidence: list[str]) -> None:
        """Display assessment evidence in the read-only evidence panel."""

        self.evidence_status.setPlainText("\n".join(evidence))
