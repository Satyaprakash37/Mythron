import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_create_app_and_main_window():
    from mythron.ui import MainWindow, create_app

    app = create_app([])
    window = MainWindow()

    assert app is not None
    assert window.windowTitle() == "MYTHRON"

    window.close()


def test_main_window_has_core_dashboard_sections():
    from PySide6.QtWidgets import QLabel

    from mythron.ui import MainWindow

    window = MainWindow()

    labels = [
        child.text()
        for child in window.findChildren(QLabel)
    ]

    assert "MYTHRON" in labels
    assert "Dashboard" in labels
    assert "System Status" in labels

    window.close()


def test_main_window_has_assessment_sections():
    from PySide6.QtWidgets import QLabel

    from mythron.ui import MainWindow

    window = MainWindow()

    labels = [
        child.text()
        for child in window.findChildren(QLabel)
    ]

    assert "Assessment" in labels
    assert "Findings" in labels
    assert "Evidence" in labels
    assert "Training Evaluation" in labels

    window.close()


def test_main_window_can_display_training_report():
    from mythron.ui import MainWindow

    window = MainWindow()

    report = {
        "passed": True,
        "summary": {
            "total": 2,
            "passed": 2,
            "failed": 0,
        },
        "failed_cases": [],
        "case_statuses": {
            "case-1": True,
            "case-2": True,
        },
    }

    window.show_training_report(report)

    assert "2 / 2 passed" in window.training_status.text()

    window.close()


def test_main_window_can_display_assessment_status():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_assessment_status(
        "Authorized local assessment ready."
    )

    assert window.assessment_status.text() == (
        "Authorized local assessment ready."
    )

    window.close()


def test_main_window_has_dashboard_panels():
    from PySide6.QtWidgets import QGroupBox

    from mythron.ui import MainWindow

    window = MainWindow()

    panel_titles = [
        panel.title()
        for panel in window.findChildren(QGroupBox)
    ]

    assert "Assessment" in panel_titles
    assert "Findings" in panel_titles
    assert "Training Evaluation" in panel_titles

    window.close()


def test_main_window_can_display_findings_and_evidence():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_findings(["Missing security header", "Information disclosure"])
    window.show_evidence(["HTTP response captured", "Header observation recorded"])

    assert "Missing security header" in window.findings_status.toPlainText()
    assert "Information disclosure" in window.findings_status.toPlainText()

    assert "HTTP response captured" in window.evidence_status.toPlainText()
    assert "Header observation recorded" in window.evidence_status.toPlainText()

    window.close()


def test_main_window_can_update_assessment_state():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.set_assessment_state("Running")

    assert window.assessment_state.text() == "Running"

    window.set_assessment_state("Completed")

    assert window.assessment_state.text() == "Completed"

    window.close()


def test_main_window_has_security_console_navigation():
    from PySide6.QtWidgets import QPushButton

    from mythron.ui import MainWindow

    window = MainWindow()

    navigation = [
        button.text()
        for button in window.findChildren(QPushButton)
    ]

    assert "Dashboard" in navigation
    assert "Assessment" in navigation
    assert "Findings" in navigation
    assert "Evidence" in navigation
    assert "Reasoning" in navigation
    assert "Training" in navigation
    assert "Activity" in navigation

    window.close()


def test_navigation_buttons_switch_console_view():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.navigate_to("Assessment")

    assert window.current_view.text() == "Assessment"

    window.navigate_to("Findings")

    assert window.current_view.text() == "Findings"

    window.close()


def test_main_window_has_security_console_header():
    from PySide6.QtWidgets import QLabel

    from mythron.ui import MainWindow

    window = MainWindow()

    labels = [
        child.text()
        for child in window.findChildren(QLabel)
    ]

    assert "MYTHRON Security Console" in labels
    assert "AUTHORIZED MODE" in labels

    window.close()


def test_main_window_uses_security_console_theme():
    from mythron.ui import MainWindow

    window = MainWindow()

    stylesheet = window.styleSheet()

    assert "background-color" in stylesheet
    assert "QGroupBox" in stylesheet
    assert "QPushButton" in stylesheet

    window.close()


def test_main_window_has_dashboard_security_status():
    from mythron.ui import MainWindow

    window = MainWindow()

    assert hasattr(window, "target_status")
    assert hasattr(window, "assessment_state")
    assert hasattr(window, "findings_count")
    assert hasattr(window, "evidence_count")

    assert window.target_status.text() == "No target configured"
    assert window.assessment_state.text() == "Ready"
    assert window.findings_count.text() == "0"
    assert window.evidence_count.text() == "0"

    window.close()


def test_findings_and_evidence_counts_update():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_findings([
        "Missing security header",
        "Information disclosure",
    ])
    window.show_evidence([
        "HTTP response captured",
        "Header observation recorded",
        "Request metadata recorded",
    ])

    assert window.findings_count.text() == "2"
    assert window.evidence_count.text() == "3"

    window.close()


def test_main_window_can_update_target_status():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_target_status("http://127.0.0.1:3000")

    assert window.target_status.text() == "http://127.0.0.1:3000"

    window.show_target_status("No target configured")

    assert window.target_status.text() == "No target configured"

    window.close()


def test_findings_and_evidence_counts_reset_when_empty():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_findings(["Finding"])
    window.show_evidence(["Evidence"])

    assert window.findings_count.text() == "1"
    assert window.evidence_count.text() == "1"

    window.show_findings([])
    window.show_evidence([])

    assert window.findings_count.text() == "0"
    assert window.evidence_count.text() == "0"

    window.close()


def test_main_window_has_console_sidebar_and_content_area():
    from PySide6.QtWidgets import QFrame

    from mythron.ui import MainWindow

    window = MainWindow()

    frames = window.findChildren(QFrame)

    object_names = [
        frame.objectName()
        for frame in frames
    ]

    assert "console_sidebar" in object_names
    assert "console_content" in object_names

    window.close()


def test_console_sidebar_has_fixed_width():
    from mythron.ui import MainWindow

    window = MainWindow()

    sidebar = window.findChild(
        __import__("PySide6.QtWidgets", fromlist=["QFrame"]).QFrame,
        "console_sidebar",
    )

    assert sidebar is not None
    assert sidebar.minimumWidth() == 220
    assert sidebar.maximumWidth() == 280

    window.close()


def test_navigation_buttons_are_inside_console_sidebar():
    from PySide6.QtWidgets import QFrame, QPushButton

    from mythron.ui import MainWindow

    window = MainWindow()

    sidebar = window.findChild(QFrame, "console_sidebar")
    assert sidebar is not None

    navigation_buttons = [
        button
        for button in sidebar.findChildren(QPushButton)
    ]

    names = [
        button.text()
        for button in navigation_buttons
    ]

    assert "Dashboard" in names
    assert "Assessment" in names
    assert "Findings" in names
    assert "Evidence" in names
    assert "Reasoning" in names
    assert "Training" in names
    assert "Activity" in names

    window.close()


def test_dashboard_has_security_status_cards():
    from PySide6.QtWidgets import QGroupBox

    from mythron.ui import MainWindow

    window = MainWindow()

    cards = [
        box
        for box in window.findChildren(QGroupBox)
        if box.objectName().startswith("status_card_")
    ]

    card_names = [
        card.objectName()
        for card in cards
    ]

    assert "status_card_target" in card_names
    assert "status_card_assessment" in card_names
    assert "status_card_findings" in card_names
    assert "status_card_evidence" in card_names

    window.close()


def test_dashboard_status_cards_have_console_object_names():
    from PySide6.QtWidgets import QGroupBox

    from mythron.ui import MainWindow

    window = MainWindow()

    expected = {
        "status_card_target",
        "status_card_assessment",
        "status_card_findings",
        "status_card_evidence",
    }

    actual = {
        card.objectName()
        for card in window.findChildren(QGroupBox)
        if card.objectName().startswith("status_card_")
    }

    assert actual == expected

    window.close()


def test_dashboard_status_cards_use_console_card_style():
    from PySide6.QtWidgets import QGroupBox

    from mythron.ui import MainWindow

    window = MainWindow()

    cards = [
        card
        for card in window.findChildren(QGroupBox)
        if card.objectName().startswith("status_card_")
    ]

    assert cards

    for card in cards:
        assert card.styleSheet() != ""

    window.close()


def test_main_window_has_console_header():
    from PySide6.QtWidgets import QFrame

    from mythron.ui import MainWindow

    window = MainWindow()

    header = window.findChild(QFrame, "console_header")

    assert header is not None

    window.close()


def test_console_header_has_security_style():
    from PySide6.QtWidgets import QFrame

    from mythron.ui import MainWindow

    window = MainWindow()

    header = window.findChild(QFrame, "console_header")

    assert header is not None
    assert header.styleSheet() != ""

    window.close()


def test_main_window_has_activity_panel():
    from PySide6.QtWidgets import QGroupBox

    from mythron.ui import MainWindow

    window = MainWindow()

    activity_panel = window.findChild(
        QGroupBox,
        "activity_panel",
    )

    assert activity_panel is not None
    assert activity_panel.title() == "Activity"

    window.close()


def test_activity_log_records_event():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.log_activity("Assessment initialized")

    assert "Assessment initialized" in window.activity_log.toPlainText()

    window.close()


def test_navigation_records_activity():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.navigate_to("Assessment")

    assert "View changed → Assessment" in window.activity_log.toPlainText()

    window.close()


def test_assessment_status_records_activity():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_assessment_status("Assessment started")

    assert "Assessment status → Assessment started" in (
        window.activity_log.toPlainText()
    )

    window.close()


def test_assessment_state_records_activity():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.set_assessment_state("Running")

    assert "Assessment state → Running" in (
        window.activity_log.toPlainText()
    )

    window.close()


def test_target_status_records_activity():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_target_status("http://127.0.0.1:3000")

    assert "Target configured → http://127.0.0.1:3000" in (
        window.activity_log.toPlainText()
    )

    window.close()


def test_findings_records_activity():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_findings(["Example finding"])

    assert "Findings updated → 1 item(s)" in (
        window.activity_log.toPlainText()
    )

    window.close()


def test_evidence_records_activity():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.show_evidence(["Example evidence"])

    assert "Evidence updated → 1 item(s)" in (
        window.activity_log.toPlainText()
    )

    window.close()


def test_activity_log_preserves_event_order():
    from mythron.ui import MainWindow

    window = MainWindow()

    window.log_activity("First event")
    window.log_activity("Second event")

    log = window.activity_log.toPlainText()

    assert log.index("First event") < log.index("Second event")

    window.close()

def test_main_window_can_attach_assessment_controller():
    from mythron.ui import MainWindow

    class FakeController:
        target = "http://127.0.0.1:3000"
        status = type("Status", (), {"value": "CREATED"})()

    window = MainWindow()
    controller = FakeController()

    window.attach_controller(controller)

    assert window.assessment_controller is controller
    assert window.target_status.text() == "http://127.0.0.1:3000"

    window.close()

def test_main_window_can_start_attached_assessment():
    from mythron.ui import MainWindow

    class FakeController:
        target = "http://127.0.0.1:3000"
        status = type("Status", (), {"value": "CREATED"})()

        def start(self):
            self.status = type("Status", (), {"value": "ACTIVE"})()

    window = MainWindow()
    controller = FakeController()

    window.attach_controller(controller)
    window.start_assessment()

    assert controller.status.value == "ACTIVE"
    assert "ACTIVE" in window.assessment_status.text()

    window.close()

def test_main_window_can_execute_attached_assessment():
    from mythron.ui import MainWindow
    from mythron.assessment_engine import AssessmentExecution
    from mythron.approaches import AttemptStatus
    from mythron.executors import ExecutionResult

    class FakeController:
        target = "http://127.0.0.1:3000"
        status = type("Status", (), {"value": "CREATED"})()

        def start(self):
            self.status = type("Status", (), {"value": "ACTIVE"})()

        def execute(self, capability_name, approach_name, target):
            return AssessmentExecution(
                allowed=True,
                result=ExecutionResult(
                    status=AttemptStatus.SUCCEEDED,
                    result="controlled browser inspection",
                    observations=["local target observed"],
                ),
            )

    window = MainWindow()
    controller = FakeController()

    window.attach_controller(controller)
    window.start_assessment()

    result = window.execute_assessment()

    assert result.allowed is True
    assert result.result.status == AttemptStatus.SUCCEEDED
    assert "SUCCEEDED" in window.assessment_status.text()

    window.close()

def test_main_window_can_configure_assessment_target():
    from mythron.ui import MainWindow

    class FakeController:
        target = "http://127.0.0.1:3000"
        status = type("Status", (), {"value": "CREATED"})()

        def configure_target(self, target):
            self.target = target

    window = MainWindow()
    controller = FakeController()

    window.attach_controller(controller)
    window.configure_target("http://127.0.0.1:3000")

    assert controller.target == "http://127.0.0.1:3000"
    assert window.target_status.text() == "http://127.0.0.1:3000"

    window.close()
