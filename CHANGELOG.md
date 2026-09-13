# MYTHRON — CHANGELOG

All notable changes to MYTHRON will be documented in this file.
Newest entries first.

## [Phase 1 Complete] — 2026-09-13

### Added

- src/mythron/reasoning.py — ReasoningCore class wrapping Google Gemini API
- tests/test_reasoning.py — 5 tests for reasoning core (all PASS)
- scripts/setup_env.py — secure .env setup helper using getpass
- Python venv at .venv/ with google-genai SDK v2.23.0

### Decisions

- LLM provider: Google Gemini
- Default model: gemini-3.6-flash (gemini-2.5-flash deprecated for new users as of 2026-09-13)
- API key stored in .env (permissions 600, gitignored)
- Python venv at .venv/ for isolated dependencies
- Single-turn prompt-to-response for Phase 1; multi-turn deferred to Phase 2

### Verified

- CLI smoke test: python -m mythron.reasoning returns HELLO FROM MYTHRON (EXIT 0)
- Test suite: 5/5 tests passing (1 real API call)
- 55 Gemini models available via API key

## [Phase 0 Complete] — 2026-09-13

### Completed

- Project directory structure at ~/mythron/ with subdirectories: docs, logs, scripts, src, tests
- Documentation baseline: README.md, PROJECT_STATUS.md, ARCHITECTURE.md, DEVELOPMENT_HANDOFF.md, CHANGELOG.md, TODO.md
- Python package mythron (v0.0.1) with health_check() entry point at src/mythron/main.py
- Smoke tests at tests/test_basic.py — 2/2 PASS
- Git repository initialized on branch main
- First commit: 2b9cdfa "Phase 0: project bootstrap"
- Second commit: 1e6e998 "Phase 0: mark bootstrap complete"

### Decisions

- Phase 1 AI core will use API-based reasoning (no local CUDA/ROCm available)
- Branch name set to main (modern convention, renamed from default master)

### Environment

- Kali GNU/Linux Rolling 2026.3, kernel 7.0.12, x86_64
- Python 3.14.6, pip 26.1.2, Git 2.53.0
- Intel i3-1005G1, 11 Gi RAM, Intel Iris Plus G1 (no CUDA)
