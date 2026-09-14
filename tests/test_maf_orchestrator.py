"""Tests for the JARVIS orchestration boundary."""

from __future__ import annotations

import asyncio
import unittest

from jarvis.core import Agent
from jarvis.intelligence import (
    Model,
    ModelCapability,
    ModelControlConstraints,
    ModelRegistry,
    ModelType,
    ModelUsageRequest,
    ModelUsageStrategy,
)
from jarvis.orchestrator import JarvisOrchestrator, OrchestrationRequest


class FakeHermes:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def chat(self, message: str, **kwargs: object) -> str:
        self.calls.append({"message": message, **kwargs})
        return f"Hermes: {message}"


class MafOrchestratorTests(unittest.TestCase):
    def _orchestrator(self) -> tuple[JarvisOrchestrator, FakeHermes]:
        hermes = FakeHermes()
        orchestrator = JarvisOrchestrator(hermes)  # type: ignore[arg-type]
        orchestrator.register_agent(
            Agent(id="agent-1", name="Test Agent", role="test", configuration={"model": "agent-model"})
        )
        orchestrator.lifecycle.activate("agent-1")
        return orchestrator, hermes

    def test_request_is_routed_through_maf_to_active_agent(self) -> None:
        orchestrator, hermes = self._orchestrator()
        request = OrchestrationRequest(
            message="test MAF",
            model="test-model",
            session_id="session-1",
            task_id="task-1",
            max_iterations=7,
            timeout=12.5,
            agent_id="agent-1",
        )

        result = asyncio.run(orchestrator.run(request))

        self.assertEqual(result, "Hermes: test MAF")
        self.assertEqual(len(hermes.calls), 1)
        self.assertEqual(hermes.calls[0]["model"], "test-model")
        self.assertEqual(hermes.calls[0]["session_id"], "session-1")
        self.assertEqual(hermes.calls[0]["task_id"], "task-1")
        self.assertEqual(hermes.calls[0]["max_iterations"], 7)
        self.assertEqual(hermes.calls[0]["timeout"], 12.5)

    def test_agent_configuration_provides_default_model(self) -> None:
        orchestrator, hermes = self._orchestrator()
        request = OrchestrationRequest(message="use configured model", agent_id="agent-1")

        asyncio.run(orchestrator.run(request))

        self.assertEqual(hermes.calls[0]["model"], "agent-model")

    def test_model_intelligence_is_resolved_before_maf_execution(self) -> None:
        hermes = FakeHermes()
        models = ModelRegistry()
        models.register(
            Model(
                id="quality-model",
                name="Quality model",
                provider="test-provider",
                model_id="provider-quality-v1",
                model_type=ModelType.LLM,
                capabilities=(ModelCapability.TEXT_GENERATION,),
            )
        )
        orchestrator = JarvisOrchestrator(hermes, model_registry=models)  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent", role="test"))
        orchestrator.lifecycle.activate("agent-1")

        request = OrchestrationRequest(
            message="route through intelligence",
            agent_id="agent-1",
            model_usage=ModelUsageRequest(strategy=ModelUsageStrategy.QUALITY),
        )

        asyncio.run(orchestrator.run(request))

        self.assertEqual(hermes.calls[0]["model"], "provider-quality-v1")

    def test_model_controls_are_applied_before_execution(self) -> None:
        hermes = FakeHermes()
        models = ModelRegistry()
        models.register(
            Model(
                id="blocked-model",
                name="Blocked model",
                provider="blocked-provider",
                model_id="provider-blocked-v1",
                model_type=ModelType.LLM,
                capabilities=(ModelCapability.TEXT_GENERATION,),
            )
        )
        orchestrator = JarvisOrchestrator(hermes, model_registry=models)  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent", role="test"))
        orchestrator.lifecycle.activate("agent-1")

        request = OrchestrationRequest(
            message="must be rejected",
            agent_id="agent-1",
            model_usage=ModelUsageRequest(strategy=ModelUsageStrategy.BALANCED),
            model_controls=ModelControlConstraints(allowed_providers=("allowed-provider",)),
        )

        with self.assertRaises(LookupError):
            asyncio.run(orchestrator.run(request))
        self.assertEqual(hermes.calls, [])

    def test_inactive_agent_cannot_be_executed(self) -> None:
        hermes = FakeHermes()
        orchestrator = JarvisOrchestrator(hermes)  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent"))

        with self.assertRaises(ValueError):
            asyncio.run(
                orchestrator.run(
                    OrchestrationRequest(message="must not run", agent_id="agent-1")
                )
            )
        self.assertEqual(hermes.calls, [])


if __name__ == "__main__":
    unittest.main()
