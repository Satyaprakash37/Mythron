from mythron.approaches import AttemptStatus
from mythron.executors import MockApproachExecutor
from mythron.orchestrator import AgentOrchestrator
from mythron.states import TaskState


def test_adaptive_path_continues_after_failure():
    executor = MockApproachExecutor(
        fail_names={"recon_port_scan"}
    )

    orchestrator = AgentOrchestrator(
        reasoning_core=None,
        executor=executor,
        max_attempts=10,
    )

    status = orchestrator.run(
        objective="Assess authorized target example.com",
        scope="authorized testing only",
    )

    assert status == "COMPLETED"
    assert orchestrator.state == TaskState.COMPLETED

    attempts = orchestrator.history.all_attempts()

    assert len(attempts) == 2
    assert attempts[0].status == AttemptStatus.FAILED
    assert attempts[1].status == AttemptStatus.SUCCEEDED

    assert len(orchestrator.history.approaches_failed()) == 1
    assert len(orchestrator.history.approaches_succeeded()) == 1



def test_successful_lifecycle_includes_validation_and_evidence():
    executor = MockApproachExecutor(
        fail_names={"recon_port_scan"}
    )

    orchestrator = AgentOrchestrator(
        reasoning_core=None,
        executor=executor,
        max_attempts=10,
    )

    status = orchestrator.run(
        objective="Assess authorized target example.com",
        scope="authorized testing only",
    )

    assert status == "COMPLETED"

    history = orchestrator._state.history()

    assert history == [
        (TaskState.TASK_RECEIVED, TaskState.TARGET_SCOPE_DEFINED),
        (TaskState.TARGET_SCOPE_DEFINED, TaskState.RECON),
        (TaskState.RECON, TaskState.DISCOVERY),
        (TaskState.DISCOVERY, TaskState.ANALYSIS),
        (TaskState.ANALYSIS, TaskState.FINDINGS),
        (TaskState.FINDINGS, TaskState.VALIDATION_REQUESTED),
        (TaskState.VALIDATION_REQUESTED, TaskState.VALIDATING),
        (TaskState.VALIDATING, TaskState.EVIDENCE_COLLECTION),
        (TaskState.EVIDENCE_COLLECTION, TaskState.REPORTING),
        (TaskState.REPORTING, TaskState.COMPLETED),
    ]


def test_restore_supports_validation_and_evidence_states():
    orchestrator = AgentOrchestrator(
        reasoning_core=None,
        executor=MockApproachExecutor(),
    )

    orchestrator._restore_state(TaskState.EVIDENCE_COLLECTION.value)

    assert orchestrator.state == TaskState.EVIDENCE_COLLECTION
