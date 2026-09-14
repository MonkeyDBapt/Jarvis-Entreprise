# Phase 3.6 — Cycle de vie des agents

## Decision

Step 3.6 introduces a JARVIS-owned `AgentLifecycleManager` for the lifecycle of registered agent definitions.

The lifecycle is deliberately separate from runtime execution. An `AgentLifecycleState` describes the organizational availability of an agent definition; it does not mean that Hermes, MAF, or another runtime process is currently running.

### States

```text
REGISTERED → ACTIVE ↔ INACTIVE → RETIRED
      └──────────────────────→ RETIRED
```

- `REGISTERED`: known to the lifecycle manager and not yet activated;
- `ACTIVE`: lifecycle-enabled and eligible for future execution/routing layers;
- `INACTIVE`: deliberately disabled without removing the agent definition;
- `RETIRED`: permanently removed from active lifecycle use.

### Transition rules

- `register()` validates that the agent exists in `AgentRegistry` and starts it at `REGISTERED`;
- `activate()` allows `REGISTERED → ACTIVE` and `INACTIVE → ACTIVE`;
- `deactivate()` allows `ACTIVE → INACTIVE`;
- `retire()` allows `REGISTERED → RETIRED` and `INACTIVE → RETIRED`;
- retired agents have no transition back to an active state;
- unknown agents and invalid transitions are rejected explicitly.

### Responsibility boundary

3.6 manages lifecycle state only. It does not:

- start or stop a runtime process;
- invoke Hermes or MAF;
- route tasks;
- grant permissions;
- apply governance;
- manage messaging/events;
- implement specialized agent logic.

This preserves the separation established by Phase 2 and the preceding Phase 3 steps.

### Validation

`tests/test_agent_lifecycle.py` covers initial registration, activation/deactivation, reactivation, terminal retirement, invalid transitions, unknown agents, and duplicate lifecycle registration.

GitHub Actions `Validation` run #40 on commit `d9243df0944a4a7c842597cbac5fe05cdd4096f6` completed successfully on Python 3.10, 3.11, 3.12, and 3.13.

**3.6 — Cycle de vie : VALIDÉE.**
