import asyncio
import unittest

from jarvis.core import Agent, Memory, MemoryType
from jarvis.interfaces.memory_context import MemoryContext, MemoryContextInjector
from jarvis.interfaces.memory_retriever import MemorySearchResult
from jarvis.orchestrator import JarvisOrchestrator, OrchestrationRequest


class FakeHermes:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def chat(self, message: str, **kwargs: object) -> str:
        self.calls.append({"message": message, **kwargs})
        return f"Hermes: {message}"


class FakeMemoryInjector(MemoryContextInjector):
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[tuple[str, int]] = []

    def build_context(self, query: str, *, limit: int = 5) -> MemoryContext:
        self.calls.append((query, limit))
        memory = Memory(
            id="m1",
            content=self.text,
            memory_type=MemoryType.CONTEXTUAL,
            scope="project",
        )
        return MemoryContext(
            query=query,
            memories=(MemorySearchResult(memory=memory, score=1.0),),
            text=self.text,
        )


class MemoryOrchestratorIntegrationTests(unittest.TestCase):
    def test_memory_context_is_injected_before_maf_execution(self) -> None:
        hermes = FakeHermes()
        injector = FakeMemoryInjector("Le projet utilise Python.")
        orchestrator = JarvisOrchestrator(
            hermes,  # type: ignore[arg-type]
            memory_context_injector=injector,
        )
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent"))
        orchestrator.lifecycle.activate("agent-1")

        asyncio.run(
            orchestrator.run(
                OrchestrationRequest(
                    message="Quelle technologie utilise le projet ?",
                    agent_id="agent-1",
                    memory_limit=3,
                )
            )
        )

        self.assertEqual(injector.calls, [("Quelle technologie utilise le projet ?", 3)])
        sent_message = str(hermes.calls[0]["message"])
        self.assertIn("<jarvis_memory_context>", sent_message)
        self.assertIn("Le projet utilise Python.", sent_message)
        self.assertTrue(sent_message.endswith("Quelle technologie utilise le projet ?"))

    def test_orchestrator_without_memory_preserves_original_message(self) -> None:
        hermes = FakeHermes()
        orchestrator = JarvisOrchestrator(hermes)  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent"))
        orchestrator.lifecycle.activate("agent-1")

        asyncio.run(
            orchestrator.run(
                OrchestrationRequest(message="message direct", agent_id="agent-1")
            )
        )

        self.assertEqual(hermes.calls[0]["message"], "message direct")

    def test_invalid_memory_limit_is_rejected(self) -> None:
        orchestrator = JarvisOrchestrator(FakeHermes())  # type: ignore[arg-type]
        orchestrator.register_agent(Agent(id="agent-1", name="Test Agent"))
        orchestrator.lifecycle.activate("agent-1")

        with self.assertRaises(ValueError):
            asyncio.run(
                orchestrator.run(
                    OrchestrationRequest(message="invalid", agent_id="agent-1", memory_limit=0)
                )
            )


if __name__ == "__main__":
    unittest.main()
