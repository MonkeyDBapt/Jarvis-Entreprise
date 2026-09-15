"""Microsoft Agent Framework orchestration layer for JARVIS Enterprise."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

from jarvis.communication import (
    ChannelKind,
    CommunicationMessage,
    CommunicationRouter,
    MessageKind,
)
from jarvis.core import (
    Agent,
    AgentAssignmentManager,
    AgentLifecycleManager,
    AgentRegistry,
    AgentSelectionCriteria,
    AuthorizationEvaluator,
    AuthorizationRequest,
    AutonomyPolicy,
    CapabilityAssignmentManager,
    CapabilityExecutor,
    CapabilityRegistry,
    ControlDecision,
    ControlEvaluator,
    ControlOutcome,
    Organization,
    OrganizationManager,
    PermissionAssignmentRegistry,
    SecurityController,
    SecurityControlledExecutor,
)
from jarvis.intelligence import (
    ModelControlConstraints,
    ModelRegistry,
    ModelRouter,
    ModelUsageRequest,
)
from jarvis.interfaces import AgentRuntime
from jarvis.interfaces.memory_context import MemoryContextInjector
from jarvis.observability import (
    AuditEvent,
    AuditEventType,
    AuditRecorder,
    HealthCheck,
    HealthCheckResult,
    HealthRegistry,
    HealthStatus,
    LogLevel,
    MetricDefinition,
    MetricKind,
    MetricRegistry,
    StructuredLogger,
    TraceContext,
    TraceRecorder,
    TraceSpan,
    TraceStatus,
)
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
    memory_limit: int = 5
    model_usage: ModelUsageRequest | None = None
    model_controls: ModelControlConstraints | None = None
    subject_id: str | None = None
    action: str | None = None
    resource: str | None = None
    authorization_scope: str | None = None
    autonomy_policy: AutonomyPolicy | None = None
    correlation_id: str | None = None
    trace_id: str | None = None


@dataclass(frozen=True)
class ResolvedAgentRequest:
    """Execution request after organizational and model resolution."""

    request: OrchestrationRequest
    agent: Agent
    context: str = ""
    resolved_model: str = ""


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
        message = request.request.message
        if request.context:
            message = (
                "<jarvis_memory_context>\n"
                f"{request.context}\n"
                "</jarvis_memory_context>\n\n"
                f"{message}"
            )

        response = await asyncio.to_thread(
            self.runtime.chat,
            message,
            model=request.resolved_model,
            session_id=request.request.session_id,
            task_id=request.request.task_id,
            max_iterations=request.request.max_iterations,
            timeout=request.request.timeout,
        )
        await ctx.yield_output(response)


class JarvisOrchestrator:
    """JARVIS orchestration entry point for agents, intelligence, memory, capabilities, communication, control and observability."""

    def __init__(
        self,
        runtime: AgentRuntime | None = None,
        *,
        organization: Organization | None = None,
        registry: AgentRegistry | None = None,
        lifecycle: AgentLifecycleManager | None = None,
        assignment: AgentAssignmentManager | None = None,
        capability_registry: CapabilityRegistry | None = None,
        capability_assignment: CapabilityAssignmentManager | None = None,
        capability_executor: CapabilityExecutor | None = None,
        security_controller: SecurityController | None = None,
        memory_context_injector: MemoryContextInjector | None = None,
        model_registry: ModelRegistry | None = None,
        model_router: ModelRouter | None = None,
        communication_router: CommunicationRouter | None = None,
        permission_registry: PermissionAssignmentRegistry | None = None,
        authorization_evaluator: AuthorizationEvaluator | None = None,
        control_evaluator: ControlEvaluator | None = None,
        logger: StructuredLogger | None = None,
        metric_registry: MetricRegistry | None = None,
        trace_recorder: TraceRecorder | None = None,
        audit_recorder: AuditRecorder | None = None,
        health_registry: HealthRegistry | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.organization = OrganizationManager(
            organization or Organization(id="jarvis", name="JARVIS Enterprise")
        )
        self.lifecycle = lifecycle or AgentLifecycleManager(self.registry)
        self.assignment = assignment or AgentAssignmentManager(self.registry, self.organization)

        self.capability_registry = capability_registry or CapabilityRegistry()
        self.capability_assignment = capability_assignment or CapabilityAssignmentManager(
            self.registry, self.capability_registry
        )
        self.capability_executor = capability_executor or CapabilityExecutor(
            self.registry, self.capability_registry, self.capability_assignment
        )
        self.security_controller = security_controller or SecurityController()
        self.security_executor = SecurityControlledExecutor(
            self.capability_executor, self.security_controller
        )

        self.memory_context_injector = memory_context_injector
        self.model_registry = model_registry
        self.model_router = model_router or (
            ModelRouter(model_registry) if model_registry is not None else None
        )
        if self.model_router is not None and self.model_registry is None:
            raise ValueError("Un routeur de modèles nécessite un registre de modèles.")

        self.communication_router = communication_router
        self.permission_registry = permission_registry
        self.authorization_evaluator = authorization_evaluator or (
            AuthorizationEvaluator(permission_registry)
            if permission_registry is not None
            else None
        )
        if self.authorization_evaluator is not None and self.permission_registry is None:
            raise ValueError("Un évaluateur d'autorisation nécessite un registre de permissions.")
        self.control_evaluator = control_evaluator or ControlEvaluator()

        self.logger = logger or StructuredLogger("orchestrator")
        self.metric_registry = metric_registry or MetricRegistry()
        self.trace_recorder = trace_recorder or TraceRecorder()
        self.audit_recorder = audit_recorder or AuditRecorder()
        self.health_registry = health_registry or HealthRegistry()
        self._register_observability_metrics()
        self._register_health_checks()

        self.hermes_executor = HermesExecutor(runtime)
        self.workflow = WorkflowBuilder(start_executor=self.hermes_executor).build()

    def _register_observability_metrics(self) -> None:
        definitions = (
            MetricDefinition("jarvis.orchestrator.requests", MetricKind.COUNTER),
            MetricDefinition("jarvis.orchestrator.successes", MetricKind.COUNTER),
            MetricDefinition("jarvis.orchestrator.failures", MetricKind.COUNTER),
            MetricDefinition("jarvis.orchestrator.duration_seconds", MetricKind.HISTOGRAM, unit="s"),
        )
        for definition in definitions:
            self.metric_registry.register(definition)

    def _register_health_checks(self) -> None:
        self.health_registry.register(
            HealthCheck(
                name="orchestrator.workflow",
                component="orchestrator",
                description="MAF workflow is constructed and ready for execution.",
                critical=True,
            )
        )
        self.health_registry.record(
            HealthCheckResult(
                name="orchestrator.workflow",
                component="orchestrator",
                status=HealthStatus.HEALTHY,
                message="MAF workflow is initialized.",
                critical=True,
            )
        )

    def health(self):
        """Return the current orchestrator/system health snapshot."""
        return self.health_registry.snapshot()

    def metrics(self):
        """Return the current orchestrator metric snapshots."""
        return self.metric_registry.snapshot()

    def traces(self, trace_id: str | None = None):
        """Return recorded orchestration traces, optionally filtered by trace id."""
        return self.trace_recorder.spans(trace_id)

    def audit_events(self, *, correlation_id: str | None = None, trace_id: str | None = None):
        """Return recorded orchestration audit events."""
        return self.audit_recorder.events(correlation_id=correlation_id, trace_id=trace_id)

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

    def resolve_model(self, request: OrchestrationRequest, agent: Agent) -> str:
        """Resolve the provider model identifier before entering the MAF workflow."""
        configured_model = str(agent.configuration.get("model", ""))
        if request.model_usage is None:
            return request.model or configured_model
        if self.model_router is None:
            raise ValueError("Le routage de modèle nécessite un ModelRegistry configuré.")

        selection = request.model_usage.to_selection_request()
        result = self.model_router.select(selection, request.model_controls)
        return result.model.model_id

    def evaluate_control(
        self,
        *,
        subject_id: str,
        action: str,
        resource: str,
        scope: str,
        autonomy_policy: AutonomyPolicy | None = None,
    ) -> ControlDecision:
        """Evaluate authorization and autonomy before an orchestrated execution."""
        if self.authorization_evaluator is None:
            raise RuntimeError("L'intégration des permissions n'est pas configurée.")

        authorization = self.authorization_evaluator.evaluate(
            AuthorizationRequest(
                subject_id=subject_id,
                action=action,
                resource=resource,
                scope=scope,
            )
        )
        return self.control_evaluator.evaluate(authorization, autonomy_policy)

    def _enforce_control(self, request: OrchestrationRequest) -> ControlDecision | None:
        fields = (
            request.subject_id,
            request.action,
            request.resource,
            request.authorization_scope,
        )
        if all(value is None for value in fields):
            return None
        if any(value is None for value in fields):
            raise ValueError(
                "Une requête de contrôle doit fournir subject_id, action, resource et authorization_scope."
            )

        decision = self.evaluate_control(
            subject_id=request.subject_id,
            action=request.action,
            resource=request.resource,
            scope=request.authorization_scope,
            autonomy_policy=request.autonomy_policy,
        )
        if decision.outcome is ControlOutcome.DENIED:
            raise PermissionError(decision.authorization.reason)
        if decision.requires_human_control:
            raise PermissionError(
                "L'exécution orchestrée nécessite une validation ou une supervision humaine."
            )
        return decision

    def register_capability_handler(self, capability_id: str, handler) -> None:
        """Register one concrete implementation at the capability boundary."""
        self.capability_executor.register_handler(capability_id, handler)

    def execute_capability(
        self,
        subject_id: str,
        agent_id: str,
        capability_id: str,
        payload=None,
    ):
        """Authorize and execute an assigned capability through the orchestration boundary."""
        agent = self.registry.get(agent_id)
        if not self.lifecycle.is_active(agent.id):
            raise ValueError(f"L'agent '{agent.id}' n'est pas actif.")
        return self.security_executor.execute(subject_id, agent_id, capability_id, payload)

    def can_execute_capability(
        self,
        subject_id: str,
        agent_id: str,
        capability_id: str,
    ) -> bool:
        """Check security, lifecycle, assignment and implementation readiness."""
        agent = self.registry.get(agent_id)
        if not self.lifecycle.is_active(agent.id):
            return False
        return self.security_executor.can_execute(subject_id, agent_id, capability_id)

    def build_memory_context(self, request: OrchestrationRequest) -> str:
        """Build prompt-ready memory context when a memory injector is configured."""
        if request.memory_limit < 1:
            raise ValueError("La limite de mémoire doit être supérieure à zéro.")
        if self.memory_context_injector is None:
            return ""
        return self.memory_context_injector.build_context(
            request.message,
            limit=request.memory_limit,
        ).text

    def _require_communication_router(self) -> CommunicationRouter:
        if self.communication_router is None:
            raise RuntimeError("L'intégration communication n'est pas configurée.")
        return self.communication_router

    async def run_and_reply(
        self,
        request: OrchestrationRequest,
        *,
        sender_id: str,
        recipient_id: str,
        correlation_id: str | None = None,
        channel: ChannelKind = ChannelKind.MESSAGE,
    ) -> CommunicationMessage:
        """Run an orchestration request and route its response through communication."""
        response = await self.run(request)
        message = CommunicationMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={"response": response},
            kind=MessageKind.RESPONSE,
            correlation_id=correlation_id,
            session_id=request.session_id,
            task_id=request.task_id,
        )
        self._require_communication_router().route_message(message, channel)
        return message

    async def run(self, request: OrchestrationRequest) -> str:
        """Resolve control, agent and model, inject memory context, execute through MAF, and observe the operation."""
        started = datetime.now(timezone.utc)
        trace_context = TraceContext.new(trace_id=request.trace_id)
        correlation_id = request.correlation_id or trace_context.trace_id
        self.metric_registry.increment("jarvis.orchestrator.requests")
        self.audit_recorder.record(
            AuditEvent.new(
                AuditEventType.REQUESTED,
                "orchestrate",
                "orchestrator",
                agent_id=request.agent_id,
                task_id=request.task_id,
                correlation_id=correlation_id,
                trace_id=trace_context.trace_id,
            )
        )
        self.logger.log(
            LogLevel.INFO,
            "Orchestration request started",
            event="orchestration.started",
            correlation_id=correlation_id,
            agent_id=request.agent_id,
            task_id=request.task_id,
        )
        try:
            self._enforce_control(request)
            agent = self.resolve_agent(request)
            context = self.build_memory_context(request)
            resolved_model = self.resolve_model(request, agent)
            response = await self.workflow.run(
                ResolvedAgentRequest(
                    request=request,
                    agent=agent,
                    context=context,
                    resolved_model=resolved_model,
                )
            )
            outputs = response.get_outputs()
            if not outputs:
                raise RuntimeError("Le workflow M.A.F. n'a produit aucune sortie.")
            result = str(outputs[-1])
            self.metric_registry.increment("jarvis.orchestrator.successes")
            self.audit_recorder.record(
                AuditEvent.new(
                    AuditEventType.COMPLETED,
                    "orchestrate",
                    "orchestrator",
                    agent_id=agent.id,
                    task_id=request.task_id,
                    correlation_id=correlation_id,
                    trace_id=trace_context.trace_id,
                    outcome="success",
                )
            )
            self.logger.log(
                LogLevel.INFO,
                "Orchestration request completed",
                event="orchestration.completed",
                correlation_id=correlation_id,
                agent_id=agent.id,
                task_id=request.task_id,
            )
            return result
        except Exception as exc:
            self.metric_registry.increment("jarvis.orchestrator.failures")
            self.audit_recorder.record(
                AuditEvent.new(
                    AuditEventType.FAILED,
                    "orchestrate",
                    "orchestrator",
                    agent_id=request.agent_id,
                    task_id=request.task_id,
                    correlation_id=correlation_id,
                    trace_id=trace_context.trace_id,
                    outcome="failure",
                    reason=str(exc),
                )
            )
            self.logger.log(
                LogLevel.ERROR,
                "Orchestration request failed",
                event="orchestration.failed",
                correlation_id=correlation_id,
                agent_id=request.agent_id,
                task_id=request.task_id,
                metadata={"error_type": type(exc).__name__, "error": str(exc)},
            )
            raise
        finally:
            ended = datetime.now(timezone.utc)
            duration = (ended - started).total_seconds()
            self.metric_registry.observe(
                "jarvis.orchestrator.duration_seconds",
                duration,
            )
            status = TraceStatus.ERROR if self.metric_registry.snapshot("jarvis.orchestrator.failures") and False else TraceStatus.OK
            # The trace status is corrected below from the recorded audit outcome.
            failed = any(
                event.trace_id == trace_context.trace_id and event.event_type is AuditEventType.FAILED
                for event in self.audit_recorder.events(trace_id=trace_context.trace_id)
            )
            status = TraceStatus.ERROR if failed else TraceStatus.OK
            self.trace_recorder.record(
                TraceSpan(
                    context=trace_context,
                    operation="orchestrate",
                    component="orchestrator",
                    started_at=started,
                    ended_at=ended,
                    status=status,
                    attributes={"correlation_id": correlation_id},
                )
            )


__all__ = [
    "HermesExecutor",
    "JarvisOrchestrator",
    "OrchestrationRequest",
    "ResolvedAgentRequest",
]
