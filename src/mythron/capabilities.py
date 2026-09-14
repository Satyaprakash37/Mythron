"""MYTHRON Phase 5 — Capability registry.

Capabilities describe what MYTHRON is allowed to invoke.
This module intentionally does not execute arbitrary commands.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Capability:
    """Description of a capability available to MYTHRON."""

    name: str
    description: str
    category: str
    requires_authorization: bool = True
    enabled: bool = True


class CapabilityRegistry:
    """Registry of capabilities available to the agent."""

    def __init__(self) -> None:
        self._capabilities: Dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        """Register or replace a capability by name."""
        if not capability.name.strip():
            raise ValueError("Capability name cannot be empty")

        self._capabilities[capability.name] = capability

    def get(self, name: str) -> Optional[Capability]:
        """Return a capability by name, or None if not registered."""
        return self._capabilities.get(name)

    def list_all(self) -> List[Capability]:
        """Return all registered capabilities."""
        return list(self._capabilities.values())

    def enabled(self) -> List[Capability]:
        """Return only enabled capabilities."""
        return [c for c in self._capabilities.values() if c.enabled]

    def contains(self, name: str) -> bool:
        """Return True when a capability is registered."""
        return name in self._capabilities
