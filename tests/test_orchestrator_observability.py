import asyncio
import unittest

from jarvis.core import Agent
from jarvis.orchestrator import JarvisOrchestrator, OrchestrationRequest
from jarvis.observability import AuditEventType, HealthStatus


class FakeRuntime:
    def chat(
        self,
        message: str,
        *,
        model: str = "",
        session_id: str | None = None,
        task_id: str | None = None,
        max_iterations: int = 20,
        timeout: float | None = None,
    ) -> str:
        return f"response:{message}"


class OrchestratorObservabilityTests(unittest.TestCase):
    def test_run_is_observable_end_to_end(self) -> None:
        orchestrator = JarvisOrchestrator(runtime=FakeRuntime())
        orchestrator.register_agent(Agent("agent-1", "Agent 1"))

        result = asyncio.run(
            orchestrator.run(
                OrchestrationRequest(
                    message="hello",
                    agent_id="agent-1",
                    task_id="task-1",
                    correlation_id="corr-1",
                )
            )
        )

        self.assertEqual(result, "response:hello")
        metrics = {snapshot.name: snapshot for snapshot in orchestrator.metrics()}
        self.assertEqual(metrics["jarvis.orchestrator.requests"].value, 1.0)
        self.assertEqual(metrics["jarvis.orchestrator.successes"].value, 1.0)
        self.assertEqual(metrics["jarvis.orchestrator.failures"].value, 0.0)
        self.assertEqual(metrics["jarvis.orchestrator.duration_seconds"].count, 1)

        events = orchestrator.audit_events(correlation_id="corr-1")
        self.assertEqual([event.event_type for event in events], [AuditEventType.REQUESTED, AuditEventType.COMPLETED])
        self.assertEqual(len(orchestrator.traces()), 1)
        self.assertEqual(orchestrator.traces()[0].context.trace_id, events[0].trace_id)
        self.assertEqual(orchestrator.health().status, HealthStatus.HEALTHY)

    def test_failed_run_is_observable_as_failure(self) -> None:
        orchestrator = JarvisOrchestrator(runtime=FakeRuntime())

        with self.assertRaises(LookupError):
            asyncio.run(orchestrator.run(OrchestrationRequest(message="hello")))

        metrics = {snapshot.name: snapshot for snapshot in orchestrator.metrics()}
        self.assertEqual(metrics["jarvis.orchestrator.failures"].value, 1.0)
        events = orchestrator.audit_events()
        self.assertEqual(events[-1].event_type, AuditEventType.FAILED)
        self.assertEqual(len(orchestrator.traces()), 1)


if __name__ == "__main__":
    unittest.main()
