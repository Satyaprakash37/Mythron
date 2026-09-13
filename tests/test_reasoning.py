"""Tests for MYTHRON Phase 1 reasoning core."""

import sys
from pathlib import Path

# Add src to path so mythron package can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythron.reasoning import ReasoningCore, load_api_key, DEFAULT_MODEL


def test_load_api_key_returns_non_empty_string():
    """API key must be loadable from .env or environment."""
    key = load_api_key()
    assert isinstance(key, str)
    assert len(key) >= 20
    print(f"  (key length: {len(key)} chars)")


def test_reasoning_core_can_be_instantiated():
    """ReasoningCore must be constructible without errors."""
    core = ReasoningCore()
    assert core.model == DEFAULT_MODEL
    assert core.temperature == 0.7
    assert core.max_output_tokens == 2048
    assert core._client is not None


def test_reasoning_core_rejects_empty_prompt():
    """reason() must raise ValueError for empty prompt."""
    core = ReasoningCore()
    try:
        core.reason("")
        assert False, "Should have raised ValueError for empty string"
    except ValueError:
        pass
    try:
        core.reason("   ")
        assert False, "Should have raised ValueError for whitespace-only"
    except ValueError:
        pass


def test_reasoning_core_returns_text_for_simple_prompt():
    """reason() must return non-empty text for a valid prompt."""
    core = ReasoningCore()
    response = core.reason("Reply with exactly: TEST OK")
    assert isinstance(response, str)
    assert len(response) > 0
    assert any(word in response.upper() for word in ["TEST", "OK"])


def test_reasoning_core_custom_model():
    """ReasoningCore must accept custom model parameter."""
    core = ReasoningCore(model="gemini-3.6-flash")
    assert core.model == "gemini-3.6-flash"


if __name__ == "__main__":
    print("=== MYTHRON Reasoning Core Tests ===")
    print()
    tests = [
        ("test_load_api_key_returns_non_empty_string", test_load_api_key_returns_non_empty_string),
        ("test_reasoning_core_can_be_instantiated", test_reasoning_core_can_be_instantiated),
        ("test_reasoning_core_rejects_empty_prompt", test_reasoning_core_rejects_empty_prompt),
        ("test_reasoning_core_returns_text_for_simple_prompt", test_reasoning_core_returns_text_for_simple_prompt),
        ("test_reasoning_core_custom_model", test_reasoning_core_custom_model),
    ]
    for i, (name, fn) in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] {name}")
        fn()
        print("  PASS")
        print()
    print("All tests passed.")
