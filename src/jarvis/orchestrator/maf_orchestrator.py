"""Microsoft Agent Framework orchestration layer for JARVIS Enterprise."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

from jarvis.interfaces import AgentRuntime
from jarvis.runtime import HermesAdapter


@dataclass(frozen=True)
class OrchestrationRequest:
    """Input passed through the MAF workflow to a runtime adapter."""

    message: str
    model: str = ""
    session_id: str | None = None
    task_id: str | None = None
    max_iterations: int = 20
    timeout: float | None = None


class HermesExecutor(Executor):
    """MAF executor that delegates agent execution to a JARVIS runtime interface."""

    def __init__(self, runtime: AgentRuntime | None = None, *, id: str = "hermes") -> None:
        super().__init__(id=id)
        self.runtime = runtime or HermesAdapter()

    @handler
    async def execute_request(
        self,
        request: OrchestrationRequest,
        ctx: WorkflowContext[str],
    ) -> None:
        response = await asyncio.to_thread(
            self.runtime.chat,
            request.message,
            model=request.model,
            session_id=request.session_id,
            task_id=request.task_id,
            max_iterations=request.max_iterations,
            timeout=request.timeout,
        )
        await ctx.yield_output(response)


class JarvisOrchestrator:
    """Public JARVIS orchestration entry point backed by Microsoft Agent Framework."""

    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        self.hermes_executor = HermesExecutor(runtime)
        self.workflow = WorkflowBuilder(start_executor=self.hermes_executor).build()

    async def run(self, request: OrchestrationRequest) -> str:
        """Execute one request through the MAF workflow and return its final output."""
        result = await self.workflow.run(request)
        outputs = result.get_outputs()
        if not outputs:
            raise RuntimeError("Le workflow M.A.F. n'a produit aucune sortie.")
        return str(outputs[-1])
