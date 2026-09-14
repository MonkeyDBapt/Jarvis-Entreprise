# Phase 4 — Capacités

## 4.7 — Intégration orchestrateur

### Decision

JARVIS integrates the Phase 4 capability execution domain into the existing `JarvisOrchestrator` without replacing the Phase 2 MAF/runtime path.

The orchestrator now exposes the capability path as a JARVIS-owned facade:

```text
Subject
  │
  ▼
JarvisOrchestrator
  │
  ▼
SecurityControlledExecutor
  │
  ▼
CapabilityExecutor
  │
  ▼
Capability handler
```

The existing agent orchestration path remains:

```text
OrchestrationRequest
  │
  ▼
Agent resolution / lifecycle
  │
  ▼
Microsoft Agent Framework
  │
  ▼
AgentRuntime
  │
  ▼
HermesAdapter → Hermes
```

### Responsibilities

`JarvisOrchestrator` now owns the composition of:

- agent registry and lifecycle;
- capability registry;
- capability assignment;
- capability execution;
- security-controlled execution;
- MAF agent execution.

The orchestrator does not implement capability-specific business logic. Concrete behavior remains registered as a `CapabilityExecutor` handler.

### Capability execution contract

`execute_capability(subject_id, agent_id, capability_id, payload)` performs the following checks in order:

1. the agent exists;
2. the agent is lifecycle-active;
3. the security subject is explicitly authorized;
4. the capability exists and is assigned to the agent;
5. a concrete capability handler exists;
6. the handler executes through `CapabilityExecutor`.

This preserves the Phase 4.6 default-deny security boundary and the Phase 4.4 assignment/execution boundary.

`can_execute_capability(...)` exposes the same readiness decision without executing the capability.

### Compatibility

- MAF remains the workflow engine for agent/runtime requests.
- `AgentRuntime` remains the stable runtime contract.
- Hermes remains the current runtime implementation.
- `CapabilityExecutor` remains the authoritative capability execution boundary.
- `SecurityControlledExecutor` remains the security boundary before capability execution.
- No direct capability-to-Hermes or capability-to-MAF bypass is introduced.

### Validation

`tests/test_phase_4_7_orchestrator.py` validates:

- authorized capability execution through the orchestrator;
- default-deny behavior;
- preservation of the agent-capability assignment boundary;
- rejection of inactive agents.

**4.7 — Intégration orchestrateur: VALIDÉE.**
