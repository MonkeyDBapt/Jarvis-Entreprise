# Phase 4 — Capacités

## 4.2 — Registre des capacités

### Decision

The capability registry is a JARVIS-owned domain service that indexes declarative `Capability` definitions by their stable identifier. It is deliberately independent from agent execution, runtime selection, routing, permissions, governance, messaging/events, and the organizational hierarchy.

### Registry contract

`CapabilityRegistry` provides:

- `register(capability)`: register a capability by stable `id`;
- `get(capability_id)`: retrieve a registered capability;
- `contains(capability_id)`: check whether an identifier is registered;
- `list_capabilities()`: list registered capabilities in registration order;
- `unregister(capability_id)`: remove and return a capability.

Capability identifiers are unique within the registry. Registering an existing identifier raises `ValueError`; retrieving or removing an unknown identifier raises `KeyError`.

### Responsibility boundary

The registry is an index, not an execution or discovery engine. It does not:

- execute capabilities;
- invoke MAF, `AgentRuntime`, or Hermes;
- select or assign agents;
- grant permissions or apply governance;
- route tasks;
- manage messaging/events;
- implement capability-specific tools or business logic.

The resulting separation is:

```text
CapabilityRegistry ── indexes Capability definitions
        │
        └── Capability

AgentRegistry ── indexes Agent definitions

AgentRuntime / MAF / Hermes ── execute work
```

The existing `Agent.capabilities` field remains compatible with capability identifiers. This step formalizes the capability index without yet changing agent selection, routing, authorization, or execution semantics.

### Validation

`tests/test_capability_registry.py` covers registration and lookup, duplicate rejection, registration ordering, removal, and unknown identifiers.

**4.2 — Registre des capacités: VALIDÉE.**
