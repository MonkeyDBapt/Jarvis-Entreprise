# Phase 4 — Capacités

## 4.3 — Affectation capacités / agents

### Decision

JARVIS introduces a dedicated `CapabilityAssignmentManager` to connect registered declarative capabilities with registered agent definitions.

The assignment is a domain relationship only. It does not execute a capability, select a runtime, route a task, authorize access, or invoke MAF/Hermes.

### Assignment contract

`CapabilityAssignmentManager` provides:

- `assign(agent_id, capability_id)`: assign an existing capability to an existing agent;
- `unassign(agent_id, capability_id)`: remove an existing assignment;
- `has_capability(agent_id, capability_id)`: check an assignment;
- `list_agent_capabilities(agent_id)`: list capability identifiers declared by an agent;
- `list_agents_with_capability(capability_id)`: return registered agents declaring a capability.

Both sides are validated against their respective registries. An unknown agent or capability raises `KeyError`. Assigning the same capability twice to the same agent raises `ValueError`.

Capability identifiers remain the canonical link between the `CapabilityRegistry` and the existing `Agent.capabilities` field. This preserves the Phase 3 agent contract while making the relationship explicit and validated by a dedicated domain service.

### Responsibility boundary

```text
CapabilityRegistry
        │
        ├── Capability definitions
        │
        ▼
CapabilityAssignmentManager
        │
        ├── assign / unassign
        ├── relationship queries
        │
        ▼
AgentRegistry
        │
        └── Agent definitions

AgentRuntime / MAF / Hermes
        └── execution remains separate
```

This step does not define permissions, governance, routing, scheduling, messaging/events, capability execution, or specialized tool implementations. Those concerns remain for later steps.

### Compatibility

Existing agents can continue to carry capability identifiers directly. The assignment service only accepts identifiers already registered in `CapabilityRegistry`, preventing new invalid relationships while preserving the existing declarative model.

### Validation

`tests/test_capability_assignment.py` covers assignment, unassignment, duplicate rejection, unknown agent/capability handling, capability queries, and reverse lookup.

**4.3 — Affectation capacités / agents: VALIDÉE.**
