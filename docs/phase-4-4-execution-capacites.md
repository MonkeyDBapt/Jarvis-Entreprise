# Phase 4 — Capacités

## 4.4 — Exécution des capacités

### Decision

JARVIS introduces a dedicated `CapabilityExecutor` as the execution boundary for registered capabilities.

A capability remains a declarative domain object. Its concrete behavior is supplied by a registered implementation (handler). Execution is permitted only when:

1. the agent exists in `AgentRegistry`;
2. the capability exists in `CapabilityRegistry`;
3. the capability is assigned to the agent through `CapabilityAssignmentManager`;
4. a concrete implementation is registered for the capability.

The executor then delegates the payload to that implementation and returns its result.

### Execution contract

`CapabilityExecutor` provides:

- `register_handler(capability_id, handler)`: bind one implementation to a registered capability;
- `unregister_handler(capability_id)`: remove the implementation;
- `execute(agent_id, capability_id, payload)`: validate the complete relationship and execute the capability;
- `can_execute(agent_id, capability_id)`: check whether the capability is assigned and executable.

A capability cannot be executed merely because it exists in the registry. The agent-capability relationship established in 4.3 is a required execution boundary.

### Responsibility boundary

```text
CapabilityRegistry
        │
        ▼
CapabilityAssignmentManager
        │
        ▼
CapabilityExecutor
        │
        ├── validates agent
        ├── validates capability
        ├── validates assignment
        └── delegates to implementation
                    │
                    ▼
             Capability handler
```

The executor does not embed capability-specific business logic. It also does not replace the Phase 2 runtime boundary, MAF orchestration, lifecycle management, permissions, governance, scheduling, or messaging/events. A handler may later delegate to those subsystems or to another specialized execution component without changing the capability contract.

### Compatibility

The implementation preserves the Phase 3 separation between the declarative `Agent` model and runtime execution. Existing capability identifiers remain canonical, and existing agents/registries continue to work unchanged.

### Validation

`tests/test_capability_execution.py` validates:

- execution of an assigned capability;
- rejection of unassigned execution;
- rejection when no implementation exists;
- registration and duplicate rejection of implementations;
- executable-state detection;
- unknown agent/capability handling.

**4.4 — Exécution des capacités: VALIDÉE.**
