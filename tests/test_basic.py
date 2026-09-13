"""Basic smoke tests for MYTHRON package."""

import sys
from pathlib import Path

# Add src to path so mythron package can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import_mythron():
    """Verify mythron package can be imported."""
    import mythron
    assert mythron.__version__ == "0.0.1"


def test_main_health_check():
    """Verify main.health_check is callable."""
    from mythron import main
    assert callable(main.health_check)


if __name__ == "__main__":
    test_import_mythron()
    print("test_import_mythron: PASS")
    test_main_health_check()
    print("test_main_health_check: PASS")
    print("All tests passed.")
