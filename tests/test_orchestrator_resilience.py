"""Tests for Phase 10 resilience integration at the orchestration boundary."""

from __future__ import annotations

import asyncio
import unittest

from jarvis.core import Agent
from jarvis.orchestrator import JarvisOrchestrator, OrchestrationRequest
from jarvis.resilience import (
    AnomalySeverity,
    DegradationAction,
    DegradationLevel,
    ErrorAction,
    OrchestratorResilience,
    RecoveryAction,
)


class FailingRuntime:
    def chat(self, message: str, **kwargs: object) -> str:
        raise RuntimeError("runtime unavailable")


class OrchestratorResilienceTests(unittest.TestCase):
    def _orchestrator(self) -> JarvisOrchestrator:
        orchestrator = JarvisOrchestrator(FailingRuntime())  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent", role="test"))
        orchestrator.lifecycle.activate("agent-1")
        return orchestrator

    def test_failure_is_classified_through_complete_resilience_chain(self) -> None:
        orchestrator = self._orchestrator()
        resilience = OrchestratorResilience()
        request = OrchestrationRequest(
            message="must fail",
            agent_id="agent-1",
            correlation_id="corr-10-7",
        )

        with self.assertRaises(RuntimeError):
            asyncio.run(resilience.run(orchestrator, request))

        self.assertIsNotNone(resilience.last_report)
        report = resilience.last_report
        assert report is not None
        self.assertEqual(report.anomaly.severity, AnomalySeverity.MEDIUM)
        self.assertEqual(report.error.exception_type, "RuntimeError")
        self.assertEqual(report.handling.action, ErrorAction.RETRY)
        self.assertEqual(report.recovery.action, RecoveryAction.RETRY)
        self.assertEqual(report.recovery.attempt, 1)
        self.assertEqual(report.degradation.action, DegradationAction.REDUCE)
        self.assertEqual(report.degradation.level, DegradationLevel.DEGRADED)
        self.assertEqual(report.anomaly.correlation_id, "corr-10-7")

    def test_critical_failure_maps_to_halt_and_safe_boundary(self) -> None:
        resilience = OrchestratorResilience()
        report = resilience.classify_failure(
            RuntimeError("critical runtime failure"),
            severity=AnomalySeverity.CRITICAL,
            correlation_id="critical-1",
        )

        self.assertEqual(report.handling.action, ErrorAction.HALT)
        self.assertEqual(report.recovery.action, RecoveryAction.HALT)
        self.assertTrue(report.recovery.requires_supervision)
        self.assertEqual(report.degradation.action, DegradationAction.HALT)
        self.assertEqual(report.degradation.level, DegradationLevel.HALTED)
        self.assertTrue(report.degradation.requires_supervision)

    def test_integration_does_not_retry_or_mutate_runtime(self) -> None:
        calls: list[int] = []

        class CountingRuntime:
            def chat(self, message: str, **kwargs: object) -> str:
                calls.append(1)
                raise RuntimeError("one failure")

        orchestrator = JarvisOrchestrator(CountingRuntime())  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent"))
        orchestrator.lifecycle.activate("agent-1")
        resilience = OrchestratorResilience()

        with self.assertRaises(RuntimeError):
            asyncio.run(
                resilience.run(
                    orchestrator,
                    OrchestrationRequest(message="one attempt", agent_id="agent-1"),
                )
            )

        self.assertEqual(calls, [1])


if __name__ == "__main__":
    unittest.main()
