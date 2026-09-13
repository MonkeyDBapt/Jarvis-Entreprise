"""Microsoft Agent Framework orchestration layer for JARVIS Enterprise."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

from jarvis.runtime.hermes_adapter import HermesAdapter


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
    """MAF executor that delegates agent execution to the Hermes adapter."""

    def __init__(self, hermes: HermesAdapter | None = None, *, id: str = "hermes") -> None:
        super().__init__(id=id)
        self.hermes = hermes or HermesAdapter()

    @handler
    async def execute_request(
        self,
        request: OrchestrationRequest,
        ctx: WorkflowContext[str],
    ) -> None:
        response = await asyncio.to_thread(
            self.hermes.chat,
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

    def __init__(self, hermes: HermesAdapter | None = None) -> None:
        self.hermes_executor = HermesExecutor(hermes)
        self.workflow = (
            WorkflowBuilder(start_executor=self.hermes_executor)
            .build()
        )

    async def run(self, request: OrchestrationRequest) -> str:
        """Execute one request through the MAF workflow and return its final output."""
        result = await self.workflow.run(request)
        outputs = result.get_outputs()
        if not outputs:
            raise RuntimeError("Le workflow M.A.F. n'a produit aucune sortie.")
        return str(outputs[-1])
