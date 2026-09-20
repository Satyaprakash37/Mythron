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
