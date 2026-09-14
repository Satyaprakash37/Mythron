# MYTHRON — ARCHITECTURE

Locked high-level architecture. See DEVELOPMENT_HANDOFF.md for change rules.

## High-Level Architecture

USER -> NATURAL LANGUAGE -> COMMAND/INTENT MANAGER -> AUTHORIZATION/SCOPE MANAGER -> AI MODEL (Reasoning/LLM) -> AGENT ORCHESTRATOR (Plan, Act, Observe, Analyze, Verify, Decide, Stop) -> BROWSER AGENT + DYNAMIC CODE ENGINE + SECURITY CAPABILITIES -> EXECUTION SANDBOX -> OBSERVATIONS -> SECURITY ANALYSIS -> VULNERABILITY FINDINGS -> VERIFICATION -> EVIDENCE ENGINE -> REPORTING -> STOP

## Phase Map

- Phase 0  — Project Bootstrap
- Phase 1  — AI Core
- Phase 2  — Agent Orchestrator
- Phase 3  — Memory / State
- Phase 4  — Browser Agent
- Phase 5  — Dynamic Capability Engine
- Phase 6  — Cybersecurity Assessment Engine
- Phase 7  — Controlled Validation
- Phase 8  — Evidence + Reporting
- Phase 9  — Evaluation Framework
- Phase 10 — Training / Fine-tuning
- Phase 11 — UI
- Phase 12 — Public MVP
- Phase 13 — Production Infrastructure

## Adaptive Multi-Path Reasoning (Phase 2 Requirement)

MYTHRON's agent orchestrator supports adaptive multi-path reasoning. If an approach fails, the agent does NOT immediately stop. It:

1. Analyzes why the previous approach failed
2. Determines whether alternative approaches are available
3. Generates/prioritizes alternative approaches
4. Avoids repeating approaches that already failed
5. Tries the next appropriate approach
6. Observes the result
7. Continues adapting until:
   - the objective is successfully completed and verified, OR
   - no useful/authorized approaches remain, OR
   - the task reaches its defined stop condition

### Attempt History Structure

The agent maintains an explicit attempt history so it knows:
- What it tried (approach name + description)
- What happened (result)
- Why it failed (failure reason)
- What alternatives remain (untried approaches)
- Which approach is currently being evaluated (in-progress)

## Agent Loop

OBSERVE -> UNDERSTAND -> PLAN -> ACT -> OBSERVE RESULT -> ANALYZE -> VERIFY -> DECIDE -> CONTINUE OR STOP

## Agent States

TASK_RECEIVED, TARGET_SCOPE_DEFINED, RECON, DISCOVERY, ENUMERATION, ANALYSIS, FINDINGS, VALIDATION_REQUESTED, VALIDATING, EVIDENCE_COLLECTION, REPORTING, COMPLETED, STOPPED

## Hardware Constraint (Phase 1 Decision)

Dev machine: Intel i3-1005G1, 11 Gi RAM, Intel Iris Plus G1 (integrated, no CUDA/ROCm).

=> Local LLM inference is not viable. Phase 1 uses an external LLM API. Revisit when dedicated GPU infrastructure is available (Phase 13).

## Change Rule

Architecture is LOCKED. Small implementation details may change. Major changes require: explanation, alternative, consequence analysis, and explicit human approval before implementation.

### Approach Selection Logic

Before selecting the next approach, the agent reasons about:
- Relevance: Does this approach address the objective?
- Authorization: Is this approach within the authorized scope?
- Scope: Does this approach stay within target boundaries?
- Expected value: Is the information/progress likely worth the cost?

The agent does NOT blindly try every possible action. It selects deliberately based on the above criteria.

### Stop Conditions

The adaptive loop terminates when:
1. Objective is completed AND verified, OR
2. No useful/authorized approaches remain, OR
3. Task reaches defined stop condition (e.g., max attempts, time limit), OR
4. Explicit stop signal received

### Modular Executor Interface

Approach executors implement a common interface so real cybersecurity capabilities can plug in later. Phase 2 uses a MockApproachExecutor for simulated actions. Phase 6+ will add real executors (browser, dynamic code, security tools) that implement the same interface.

This separation ensures the adaptive reasoning loop is capability-agnostic — the same loop works whether the executor is mocked or real.
