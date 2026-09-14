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
