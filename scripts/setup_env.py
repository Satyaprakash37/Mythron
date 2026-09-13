#!/usr/bin/env python3
"""Secure .env setup for MYTHRON Phase 1."""

import getpass
import os
import sys
from pathlib import Path

ENV_PATH = Path(__file__).parent.parent / ".env"


def main() -> int:
    print("=== MYTHRON .env Setup ===")
    print("Paste your Gemini API key when prompted.")
    print("Input will be HIDDEN (no characters shown).")
    print()
    key = getpass.getpass("[REDACTED]: ")
    if len(key) < 20:
        print(f"ERROR: key too short ({len(key)} chars). Aborting.")
        return 1
    ENV_PATH.write_text(f"GEMINI_API_KEY={key}\n")
    os.chmod(ENV_PATH, 0o600)
    print(f"OK: .env created with {len(key)}-char key.")
    print("Permissions: 600 (owner-only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
