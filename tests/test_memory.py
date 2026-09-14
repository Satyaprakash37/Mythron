from mythron.approaches import AttemptStatus
from mythron.memory import TaskMemory


def test_memory_save_and_load(tmp_path):
    memory = TaskMemory(str(tmp_path / "memory.json"))

    data = {
        "task_id": "test-001",
        "state": "RECON",
        "objective": "Assess authorized target",
        "observations": ["port 80 open"],
        "attempts": 1,
        "findings": [],
    }

    memory.save(data)

    assert memory.exists()
    assert memory.load() == data


def test_memory_missing_file_returns_none(tmp_path):
    memory = TaskMemory(str(tmp_path / "missing.json"))

    assert memory.exists() is False
    assert memory.load() is None


def test_memory_clear(tmp_path):
    memory = TaskMemory(str(tmp_path / "memory.json"))

    memory.save({"state": "RECON"})
    assert memory.exists()

    memory.clear()

    assert memory.exists() is False
    assert memory.load() is None


def test_memory_preserves_adaptive_agent_state(tmp_path):
    memory = TaskMemory(str(tmp_path / "memory.json"))

    data = {
        "task_id": "task-001",
        "objective": "Assess authorized target",
        "scope": "authorized testing only",
        "state": "DISCOVERY",
        "attempts": [
            {
                "approach": "recon_port_scan",
                "status": "FAILED",
                "failure_reason": "No useful result",
            },
            {
                "approach": "dns_lookup",
                "status": "SUCCEEDED",
                "result": "DNS information discovered",
            },
        ],
        "observations": [
            "First approach failed",
            "Alternative approach succeeded",
        ],
        "findings": [],
    }

    memory.save(data)
    restored = memory.load()

    assert restored["state"] == "DISCOVERY"
    assert len(restored["attempts"]) == 2
    assert restored["attempts"][0]["status"] == "FAILED"
    assert restored["attempts"][1]["status"] == "SUCCEEDED"
    assert restored["observations"][-1] == "Alternative approach succeeded"


def test_orchestrator_persists_adaptive_attempts(tmp_path):
    from mythron.executors import MockApproachExecutor
    from mythron.orchestrator import AgentOrchestrator

    memory = TaskMemory(str(tmp_path / "memory.json"))

    executor = MockApproachExecutor(
        fail_names={"recon_port_scan"}
    )

    orchestrator = AgentOrchestrator(
        reasoning_core=None,
        executor=executor,
        memory=memory,
        max_attempts=10,
    )

    status = orchestrator.run(
        objective="Assess authorized target example.com",
        scope="authorized testing only",
    )

    assert status == "COMPLETED"

    saved = memory.load()

    assert saved is not None
    assert saved["objective"] == "Assess authorized target example.com"
    assert saved["scope"] == "authorized testing only"
    assert saved["state"] == "COMPLETED"

    assert len(saved["attempts"]) == 2
    assert saved["attempts"][0]["status"] == "FAILED"
    assert saved["attempts"][1]["status"] == "SUCCEEDED"


def test_memory_load_or_empty_restores_saved_task(tmp_path):
    memory = TaskMemory(str(tmp_path / "memory.json"))

    saved = {
        "objective": "Resume authorized assessment",
        "scope": "authorized testing only",
        "state": "DISCOVERY",
        "attempts": [
            {
                "id": 1,
                "approach": "recon_port_scan",
                "status": "FAILED",
                "failure_reason": "No useful result",
                "result": "",
                "observations": ["No useful ports found"],
            }
        ],
    }

    memory.save(saved)

    restored = memory.load_or_empty()

    assert restored == saved
    assert restored["state"] == "DISCOVERY"
    assert restored["attempts"][0]["status"] == "FAILED"


def test_memory_load_or_empty_when_missing(tmp_path):
    memory = TaskMemory(str(tmp_path / "missing.json"))

    restored = memory.load_or_empty()

    assert restored == {
        "objective": "",
        "scope": "",
        "state": None,
        "attempts": [],
    }


def test_orchestrator_restores_previous_attempts(tmp_path):
    from mythron.executors import MockApproachExecutor
    from mythron.orchestrator import AgentOrchestrator

    memory = TaskMemory(str(tmp_path / "memory.json"))

    memory.save(
        {
            "objective": "Resume authorized assessment",
            "scope": "authorized testing only",
            "state": "DISCOVERY",
            "attempts": [
                {
                    "id": 1,
                    "approach": "recon_port_scan",
                    "status": "FAILED",
                    "result": "No useful result",
                    "failure_reason": "Target silent",
                    "observations": ["No useful ports"],
                }
            ],
        }
    )

    agent = AgentOrchestrator(
        reasoning_core=None,
        executor=MockApproachExecutor(),
        memory=memory,
    )

    # Register the same approaches that exist in the saved task.
    for approach in agent._default_approaches():
        agent.history.add_approach(approach)

    agent._restore_memory()

    assert agent.history.approaches_tried() == [1]
    assert agent.history.approaches_failed() == [1]
    assert len(agent.history.all_attempts()) == 1
    assert agent.history.all_attempts()[0].status == AttemptStatus.FAILED


def test_run_resume_uses_persisted_history(tmp_path):
    from mythron.executors import MockApproachExecutor
    from mythron.orchestrator import AgentOrchestrator

    memory = TaskMemory(str(tmp_path / "memory.json"))

    memory.save(
        {
            "objective": "Resume authorized assessment",
            "scope": "authorized testing only",
            "state": "DISCOVERY",
            "attempts": [
                {
                    "id": 1,
                    "approach": "recon_port_scan",
                    "status": "FAILED",
                    "result": "No useful result",
                    "failure_reason": "Target silent",
                    "observations": ["No useful ports"],
                }
            ],
        }
    )

    executor = MockApproachExecutor()

    agent = AgentOrchestrator(
        reasoning_core=None,
        executor=executor,
        memory=memory,
        max_attempts=10,
    )

    status = agent.run(
        objective="Resume authorized assessment",
        scope="authorized testing only",
        resume=True,
    )

    assert status == "COMPLETED"

    attempts = agent.history.all_attempts()

    assert len(attempts) == 2
    assert attempts[0].status == AttemptStatus.FAILED
    assert attempts[1].status == AttemptStatus.SUCCEEDED

    assert attempts[0].approach_id != attempts[1].approach_id
