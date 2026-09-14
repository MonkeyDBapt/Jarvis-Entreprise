# Phase 4 — Capacités

## 4.1 — Modèle de capacité

### Decision

JARVIS models a capability as a declarative, JARVIS-owned domain object. A capability describes what an agent is able to provide without embedding execution, routing, permissions, governance, messaging, or a concrete tool/runtime implementation.

### Capability contract

A `Capability` contains:

- `id`: stable identifier;
- `name`: human-readable name;
- `description`: optional human-readable description;
- `configuration`: generic declarative configuration reserved for capability-specific parameters.

### Responsibility boundary

The capability model is deliberately independent from execution:

```text
Agent
  │
  └── declares capability identifiers

Capability
  │
  └── describes a capability

AgentRuntime / MAF / Hermes
  └── remain responsible for execution
```

This step does not define how capabilities are discovered, registered, authorized, routed, executed, composed, or implemented. Those concerns remain available to later Phase 4 steps.

### Compatibility

The existing `Agent.capabilities` field remains a list of capability names/identifiers. The new `Capability` model therefore adds a formal declarative description without forcing a change to the Phase 3 agent contract.

### Validation

`tests/test_capability.py` validates capability identity, description, default configuration, and declarative configuration values.

**4.1 — Modèle de capacité: VALIDÉE.**
