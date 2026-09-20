"""MYTHRON Phase 11 — Desktop UI."""

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
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
        layout = QHBoxLayout(central)

        sidebar = QFrame()
        sidebar.setObjectName("console_sidebar")
        sidebar.setMinimumWidth(220)
        sidebar.setMaximumWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)

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

        sidebar_layout.addWidget(navigation_panel)
        sidebar_layout.addStretch()

        content = QFrame()
        content.setObjectName("console_content")
        content_layout = QVBoxLayout(content)

        brand = QLabel("MYTHRON")
        console_header = QLabel("MYTHRON Security Console")
        authorization = QLabel("AUTHORIZED MODE")
        self.current_view = QLabel("Dashboard")
        dashboard = QLabel("Dashboard")
        system_status = QLabel("System Status")

        self.target_status = QLabel("No target configured")
        self.findings_count = QLabel("0")
        self.evidence_count = QLabel("0")

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

        activity_panel = QGroupBox("Activity")
        activity_panel.setObjectName("activity_panel")
        activity_layout = QVBoxLayout(activity_panel)

        self.activity_log = QPlainTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setPlaceholderText("No activity recorded.")
        activity_layout.addWidget(self.activity_log)

        header = QFrame()
        header.setObjectName("console_header")
        header.setStyleSheet("""
            QFrame#console_header {
                background-color: #101820;
                border: 1px solid #304050;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.addWidget(brand)
        header_layout.addWidget(console_header)
        header_layout.addWidget(authorization)

        content_layout.addWidget(header)
        content_layout.addWidget(dashboard)
        content_layout.addWidget(system_status)

        status_grid = QGridLayout()

        card_style = """
            QGroupBox {
                background-color: #101820;
                border: 1px solid #304050;
                border-radius: 8px;
                padding: 12px;
                margin-top: 8px;
            }
        """

        target_card = QGroupBox("TARGET")
        target_card.setObjectName("status_card_target")
        target_card.setStyleSheet(card_style)
        target_layout = QVBoxLayout(target_card)
        target_layout.addWidget(self.target_status)

        assessment_card = QGroupBox("ASSESSMENT")
        assessment_card.setObjectName("status_card_assessment")
        assessment_card.setStyleSheet(card_style)
        assessment_layout_card = QVBoxLayout(assessment_card)
        assessment_layout_card.addWidget(self.assessment_state)

        findings_card = QGroupBox("FINDINGS")
        findings_card.setObjectName("status_card_findings")
        findings_card.setStyleSheet(card_style)
        findings_layout_card = QVBoxLayout(findings_card)
        findings_layout_card.addWidget(self.findings_count)

        evidence_card = QGroupBox("EVIDENCE")
        evidence_card.setObjectName("status_card_evidence")
        evidence_card.setStyleSheet(card_style)
        evidence_layout_card = QVBoxLayout(evidence_card)
        evidence_layout_card.addWidget(self.evidence_count)

        status_grid.addWidget(target_card, 0, 0)
        status_grid.addWidget(assessment_card, 0, 1)
        status_grid.addWidget(findings_card, 1, 0)
        status_grid.addWidget(evidence_card, 1, 1)

        content_layout.addLayout(status_grid)
        content_layout.addWidget(assessment_panel)
        content_layout.addWidget(findings_panel)
        content_layout.addWidget(evidence_panel)
        content_layout.addWidget(training_panel)
        content_layout.addWidget(activity_panel)

        layout.addWidget(sidebar, 1)
        layout.addWidget(content, 4)

        self.setCentralWidget(central)

    def navigate_to(self, view: str) -> None:
        """Switch the active MYTHRON console view."""

        self.current_view.setText(view)
        self.log_activity(f"View changed → {view}")

    def log_activity(self, message: str) -> None:
        """Append a controlled event to the MYTHRON activity log."""

        self.activity_log.appendPlainText(message)

    def show_training_report(self, report: dict) -> None:
        """Display a controlled training evaluation summary."""

        summary = report.get("summary", {})
        passed = summary.get("passed", 0)
        total = summary.get("total", 0)

        self.training_status.setText(
            f"{passed} / {total} passed"
        )

    def show_target_status(self, target: str) -> None:
        """Display the currently configured authorized assessment target."""

        self.target_status.setText(target)
        self.log_activity(f"Target configured → {target}")

    def show_assessment_status(self, status: str) -> None:
        """Display the current authorized assessment status."""

        self.assessment_status.setText(status)
        self.log_activity(f"Assessment status → {status}")

    def set_assessment_state(self, state: str) -> None:
        """Update the assessment lifecycle state."""

        self.assessment_state.setText(state)
        self.log_activity(f"Assessment state → {state}")

    def show_findings(self, findings: list[str]) -> None:
        """Display assessment findings in the read-only findings panel."""

        self.findings_status.setPlainText("\n".join(findings))
        self.findings_count.setText(str(len(findings)))
        self.log_activity(f"Findings updated → {len(findings)} item(s)")

    def show_evidence(self, evidence: list[str]) -> None:
        """Display assessment evidence in the read-only evidence panel."""

        self.evidence_status.setPlainText("\n".join(evidence))
        self.evidence_count.setText(str(len(evidence)))
        self.log_activity(f"Evidence updated → {len(evidence)} item(s)")
