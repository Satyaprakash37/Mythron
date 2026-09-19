import pytest

from mythron.states import (
    StateMachine,
    StateMachineError,
    TaskState,
)


def test_validation_state_transition_path():
    sm = StateMachine(TaskState.FINDINGS)

    sm.transition_to(TaskState.VALIDATION_REQUESTED)
    sm.transition_to(TaskState.VALIDATING)
    sm.transition_to(TaskState.EVIDENCE_COLLECTION)

    assert sm.current() == TaskState.EVIDENCE_COLLECTION


def test_validation_can_return_to_findings():
    sm = StateMachine(TaskState.VALIDATING)

    sm.transition_to(TaskState.FINDINGS)

    assert sm.current() == TaskState.FINDINGS


def test_validation_cannot_start_without_request():
    sm = StateMachine(TaskState.FINDINGS)

    with pytest.raises(StateMachineError):
        sm.transition_to(TaskState.VALIDATING)


def test_validation_request_cannot_skip_to_evidence():
    sm = StateMachine(TaskState.VALIDATION_REQUESTED)

    with pytest.raises(StateMachineError):
        sm.transition_to(TaskState.EVIDENCE_COLLECTION)


def test_validation_state_history_is_recorded():
    sm = StateMachine(TaskState.FINDINGS)

    sm.transition_to(TaskState.VALIDATION_REQUESTED)
    sm.transition_to(TaskState.VALIDATING)

    assert sm.history() == [
        (
            TaskState.FINDINGS,
            TaskState.VALIDATION_REQUESTED,
        ),
        (
            TaskState.VALIDATION_REQUESTED,
            TaskState.VALIDATING,
        ),
    ]
