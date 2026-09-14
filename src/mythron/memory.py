"""MYTHRON Phase 3 — Persistent task memory.

Stores task state, objective, scope, observations, attempts, and findings
in a local JSON file so MYTHRON can resume after restart.

No LLM calls and no external services.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class TaskMemory:
    """Simple JSON-backed persistent memory for MYTHRON tasks."""

    def __init__(self, path: str = "logs/memory.json") -> None:
        self.path = Path(path)

    def save(self, data: Dict[str, Any]) -> None:
        """Persist task data to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temp_path.replace(self.path)

    def load(self) -> Optional[Dict[str, Any]]:
        """Load persisted task data, or return None if absent."""
        if not self.path.exists():
            return None

        return json.loads(
            self.path.read_text(encoding="utf-8")
        )

    def load_or_empty(self) -> Dict[str, Any]:
        """Load persisted memory, returning an empty task structure if absent."""
        data = self.load()
        if data is None:
            return {
                "objective": "",
                "scope": "",
                "state": None,
                "attempts": [],
            }
        return data

    def exists(self) -> bool:
        """Return True if persistent memory exists."""
        return self.path.exists()

    def clear(self) -> None:
        """Delete persistent memory if it exists."""
        if self.path.exists():
            self.path.unlink()
