# MYTHRON — CHANGELOG

All notable changes to MYTHRON will be documented in this file.

## [Phase 0] — 2026-09-13

### Added

- Project directory structure at ~/mythron/ (docs, logs, scripts, src, tests)
- Documentation baseline: README.md, PROJECT_STATUS.md, ARCHITECTURE.md, DEVELOPMENT_HANDOFF.md, CHANGELOG.md, TODO.md

### Decisions

- Phase 1 AI core will use API-based reasoning (no local CUDA/ROCm available)

### Environment

- Kali GNU/Linux Rolling 2026.3, kernel 7.0.12, x86_64
- Python 3.14.6, pip 26.1.2, Git 2.53.0
- Intel i3-1005G1, 11 Gi RAM, Intel Iris Plus G1 (no CUDA)
