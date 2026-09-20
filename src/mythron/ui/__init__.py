"""MYTHRON Phase 11 — Desktop UI."""

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QGroupBox,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
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

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0f14;
            }

            QWidget {
                color: #d7e0ea;
                font-family: "DejaVu Sans";
                font-size: 13px;
            }

            QGroupBox {
                background-color: #111820;
                border: 1px solid #263442;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }

            QPushButton {
                background-color: #151e27;
                border: 1px solid #2d3d4d;
                border-radius: 5px;
                padding: 8px 12px;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #1d2a36;
            }

            QLabel {
                background-color: transparent;
            }

            QPlainTextEdit {
                background-color: #0d131a;
                border: 1px solid #263442;
                border-radius: 5px;
                padding: 6px;
            }
        """)

        central = QWidget()
        layout = QVBoxLayout(central)

        navigation_panel = QGroupBox("MYTHRON")
        navigation_layout = QVBoxLayout(navigation_panel)

        for name in (
            "Dashboard",
            "Assessment",
            "Findings",
            "Evidence",
            "Reasoning",
            "Training",
            "Activity",
        ):
            button = QPushButton(name)
            button.clicked.connect(
                lambda checked=False, view=name: self.navigate_to(view)
            )
            navigation_layout.addWidget(button)

        layout.addWidget(navigation_panel)

        brand = QLabel("MYTHRON")
        console_header = QLabel("MYTHRON Security Console")
        authorization = QLabel("AUTHORIZED MODE")
        self.current_view = QLabel("Dashboard")
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
        layout.addWidget(console_header)
        layout.addWidget(authorization)
        layout.addWidget(dashboard)
        layout.addWidget(system_status)
        layout.addWidget(assessment_panel)
        layout.addWidget(findings_panel)
        layout.addWidget(evidence_panel)
        layout.addWidget(training_panel)

        self.setCentralWidget(central)

    def navigate_to(self, view: str) -> None:
        """Switch the active MYTHRON console view."""

        self.current_view.setText(view)

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
