"""Tests for the Microsoft Agent Framework orchestration boundary."""

from __future__ import annotations

import asyncio
import unittest

from jarvis.orchestrator import JarvisOrchestrator, OrchestrationRequest


class FakeHermes:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def chat(self, message: str, **kwargs: object) -> str:
        self.calls.append({"message": message, **kwargs})
        return f"Hermes: {message}"


class MafOrchestratorTests(unittest.TestCase):
    def test_request_is_routed_through_maf_to_hermes(self) -> None:
        hermes = FakeHermes()
        orchestrator = JarvisOrchestrator(hermes)  # type: ignore[arg-type]
        request = OrchestrationRequest(
            message="test MAF",
            model="test-model",
            session_id="session-1",
            task_id="task-1",
            max_iterations=7,
            timeout=12.5,
        )

        result = asyncio.run(orchestrator.run(request))

        self.assertEqual(result, "Hermes: test MAF")
        self.assertEqual(len(hermes.calls), 1)
        self.assertEqual(hermes.calls[0]["model"], "test-model")
        self.assertEqual(hermes.calls[0]["session_id"], "session-1")
        self.assertEqual(hermes.calls[0]["task_id"], "task-1")
        self.assertEqual(hermes.calls[0]["max_iterations"], 7)
        self.assertEqual(hermes.calls[0]["timeout"], 12.5)


if __name__ == "__main__":
    unittest.main()
