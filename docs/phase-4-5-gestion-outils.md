# Phase 4 — Capacités

## 4.5 — Gestion des outils

### Decision

JARVIS introduces a dedicated `Tool` domain object and `ToolRegistry` to manage reusable tool definitions independently from capability execution.

A tool describes a reusable technical resource that may later support one or more capability implementations. The tool model is declarative and JARVIS-owned; it does not execute code, select agents, grant permissions, route tasks, or invoke MAF/Hermes directly.

### Tool contract

A `Tool` contains:

- `id`: stable identifier;
- `name`: human-readable name;
- `description`: optional human-readable description;
- `configuration`: generic declarative configuration reserved for tool-specific parameters.

`ToolRegistry` provides:

- `register(tool)`: register a tool by stable `id`;
- `get(tool_id)`: retrieve a registered tool;
- `contains(tool_id)`: check whether a tool is registered;
- `list_tools()`: list tools in registration order;
- `unregister(tool_id)`: remove and return a tool.

Tool identifiers are unique within the registry. Duplicate registration raises `ValueError`; unknown retrieval/removal raises `KeyError`.

### Responsibility boundary

```text
ToolRegistry
      │
      ▼
Tool definitions
      │
      └── reusable resources

CapabilityExecutor
      │
      └── remains the capability execution boundary
                 │
                 ▼
          Capability handler
```

The tool registry is intentionally not a second execution engine. It does not bypass the capability assignment/execution boundary, permissions, governance, routing, scheduling, messaging/events, MAF, or `AgentRuntime`.

This preserves the architecture established in 4.4: capabilities remain the agent-facing execution contract, while tools are reusable managed resources that capability implementations may consume later.

### Compatibility

Existing `Capability`, `CapabilityRegistry`, `CapabilityAssignmentManager`, and `CapabilityExecutor` contracts remain unchanged. No agent capability identifier is replaced by a tool identifier, and no direct tool execution path is introduced at this stage.

### Validation

`tests/test_tool.py` validates tool identity, defaults, and declarative configuration.

`tests/test_tool_registry.py` validates registration and lookup, duplicate rejection, registration ordering, removal, and unknown identifiers.

**4.5 — Gestion des outils: VALIDÉE.**
