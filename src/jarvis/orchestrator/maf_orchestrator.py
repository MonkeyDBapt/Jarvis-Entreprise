"""Microsoft Agent Framework orchestration layer for JARVIS Enterprise."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

from jarvis.core import (
    Agent,
    AgentAssignmentManager,
    AgentLifecycleManager,
    AgentRegistry,
    AgentSelectionCriteria,
    Organization,
    OrganizationManager,
)
from jarvis.interfaces import AgentRuntime
from jarvis.runtime import HermesAdapter


@dataclass(frozen=True)
class OrchestrationRequest:
    """Input passed through the JARVIS orchestration boundary."""

    message: str
    model: str = ""
    session_id: str | None = None
    task_id: str | None = None
    max_iterations: int = 20
    timeout: float | None = None
    agent_id: str | None = None
    selection: AgentSelectionCriteria | None = None


@dataclass(frozen=True)
class ResolvedAgentRequest:
    """Execution request after organizational agent resolution."""

    request: OrchestrationRequest
    agent: Agent


class HermesExecutor(Executor):
    """MAF executor that delegates execution to a JARVIS runtime interface."""

    def __init__(self, runtime: AgentRuntime | None = None, *, id: str = "hermes") -> None:
        super().__init__(id=id)
        self.runtime = runtime or HermesAdapter()

    @handler
    async def execute_request(
        self,
        request: ResolvedAgentRequest,
        ctx: WorkflowContext[str],
    ) -> None:
        response = await asyncio.to_thread(
            self.runtime.chat,
            request.request.message,
            model=request.request.model or str(request.agent.configuration.get("model", "")),
            session_id=request.request.session_id,
            task_id=request.request.task_id,
            max_iterations=request.request.max_iterations,
            timeout=request.request.timeout,
        )
        await ctx.yield_output(response)


class JarvisOrchestrator:
    """JARVIS orchestration entry point integrating organization and MAF execution."""

    def __init__(
        self,
        runtime: AgentRuntime | None = None,
        *,
        organization: Organization | None = None,
        registry: AgentRegistry | None = None,
        lifecycle: AgentLifecycleManager | None = None,
        assignment: AgentAssignmentManager | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.organization = OrganizationManager(
            organization or Organization(id="jarvis", name="JARVIS Enterprise")
        )
        self.lifecycle = lifecycle or AgentLifecycleManager(self.registry)
        self.assignment = assignment or AgentAssignmentManager(self.registry, self.organization)
        self.hermes_executor = HermesExecutor(runtime)
        self.workflow = WorkflowBuilder(start_executor=self.hermes_executor).build()

    def register_agent(self, agent: Agent) -> None:
        """Register an agent and initialize its lifecycle state."""
        self.registry.register(agent)
        self.lifecycle.register(agent.id)

    def resolve_agent(self, request: OrchestrationRequest) -> Agent:
        """Resolve exactly one active agent for an orchestration request."""
        if request.agent_id is not None:
            agent = self.registry.get(request.agent_id)
            if not self.lifecycle.is_active(agent.id):
                raise ValueError(f"L'agent '{agent.id}' n'est pas actif.")
            return agent

        candidates = self.assignment.select(request.selection)
        active = [agent for agent in candidates if self.lifecycle.is_active(agent.id)]
        if not active:
            raise LookupError("Aucun agent actif ne correspond à la requête d'orchestration.")
        if len(active) > 1:
            raise ValueError("La sélection d'orchestration correspond à plusieurs agents actifs.")
        return active[0]

    async def run(self, request: OrchestrationRequest) -> str:
        """Resolve an active organizational agent, then execute through the MAF workflow."""
        agent = self.resolve_agent(request)
        result = await self.workflow.run(ResolvedAgentRequest(request=request, agent=agent))
        outputs = result.get_outputs()
        if not outputs:
            raise RuntimeError("Le workflow M.A.F. n'a produit aucune sortie.")
        return str(outputs[-1])
