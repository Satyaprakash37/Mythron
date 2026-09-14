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

