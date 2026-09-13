"""MYTHRON Phase 0 — Health check entry point."""

import sys
import platform
from pathlib import Path


def health_check() -> int:
    """Print project health info and return 0 on success."""
    try:
        import mythron
        version = mythron.__version__
        phase = mythron.__phase__
    except ImportError as exc:
        print(f"FAIL: cannot import mythron package: {exc}")
        return 1

    print("=" * 50)
    print("MYTHRON — Phase 0 Health Check")
    print("=" * 50)
    print(f"Project:  MYTHRON")
    print(f"Version:  {version}")
    print(f"Phase:    {phase}")
    print(f"Python:   {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"CWD:      {Path.cwd()}")
    print("=" * 50)
    print("Status:   OK")
    return 0


if __name__ == "__main__":
    sys.exit(health_check())
