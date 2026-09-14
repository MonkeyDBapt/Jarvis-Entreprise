"""Lifecycle management for declarative JARVIS agents."""

from __future__ import annotations

from enum import Enum

from .agent_registry import AgentRegistry


class AgentLifecycleState(str, Enum):
    """JARVIS lifecycle state, independent from runtime execution state."""

    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class AgentLifecycleManager:
    """Manage the organizational lifecycle of registered agent definitions."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry
        self._states: dict[str, AgentLifecycleState] = {}

    def register(self, agent_id: str) -> AgentLifecycleState:
        """Register an agent in the lifecycle after validating it exists."""
        self.registry.get(agent_id)
        if agent_id in self._states:
            raise ValueError(f"L'agent '{agent_id}' est déjà enregistré dans le cycle de vie.")
        self._states[agent_id] = AgentLifecycleState.REGISTERED
        return self._states[agent_id]

    def get_state(self, agent_id: str) -> AgentLifecycleState:
        """Return the lifecycle state of a managed agent."""
        if agent_id not in self._states:
            raise KeyError(agent_id)
        return self._states[agent_id]

    def activate(self, agent_id: str) -> AgentLifecycleState:
        """Move a registered or inactive agent to the active lifecycle state."""
        state = self.get_state(agent_id)
        if state not in {AgentLifecycleState.REGISTERED, AgentLifecycleState.INACTIVE}:
            raise ValueError(f"Transition impossible depuis l'état '{state.value}'.")
        self._states[agent_id] = AgentLifecycleState.ACTIVE
        return self._states[agent_id]

    def deactivate(self, agent_id: str) -> AgentLifecycleState:
        """Move an active agent to the inactive lifecycle state."""
        state = self.get_state(agent_id)
        if state is not AgentLifecycleState.ACTIVE:
            raise ValueError(f"Transition impossible depuis l'état '{state.value}'.")
        self._states[agent_id] = AgentLifecycleState.INACTIVE
        return self._states[agent_id]

    def retire(self, agent_id: str) -> AgentLifecycleState:
        """Retire an agent permanently from the lifecycle manager."""
        state = self.get_state(agent_id)
        if state not in {AgentLifecycleState.REGISTERED, AgentLifecycleState.INACTIVE}:
            raise ValueError(f"Transition impossible depuis l'état '{state.value}'.")
        self._states[agent_id] = AgentLifecycleState.RETIRED
        return self._states[agent_id]

    def is_active(self, agent_id: str) -> bool:
        """Return whether the agent is lifecycle-active."""
        return self.get_state(agent_id) is AgentLifecycleState.ACTIVE
