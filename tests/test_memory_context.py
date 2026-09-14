import tempfile
import unittest
from pathlib import Path

from jarvis.core.memory import Memory, MemoryType
from jarvis.memory import RetrieverMemoryContextInjector, SQLiteMemoryRetriever, SQLiteMemoryStore


class MemoryContextInjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "memory.sqlite3"
        self.store = SQLiteMemoryStore(self.path)
        self.store.save(
            Memory(id="m1", content="Le projet JARVIS utilise Python.", memory_type=MemoryType.CONTEXTUAL, scope="project")
        )
        self.store.save(
            Memory(id="m2", content="La mémoire doit rester modulaire.", memory_type=MemoryType.LONG_TERM, scope="project")
        )
        self.retriever = SQLiteMemoryRetriever(self.path)

    def tearDown(self) -> None:
        self.retriever.close()
        self.store.close()
        self.tempdir.cleanup()

    def test_builds_context_from_retrieved_memories(self) -> None:
        injector = RetrieverMemoryContextInjector(self.retriever)
        context = injector.build_context("JARVIS Python")
        self.assertEqual(context.query, "JARVIS Python")
        self.assertEqual([item.memory.id for item in context.memories], ["m1"])
        self.assertIn("JARVIS utilise Python", context.text)

    def test_context_is_bounded(self) -> None:
        injector = RetrieverMemoryContextInjector(self.retriever, max_characters=20)
        context = injector.build_context("projet")
        self.assertLessEqual(len(context.text), 20)
        self.assertEqual(len(context.memories), 0)

    def test_empty_query_is_rejected(self) -> None:
        injector = RetrieverMemoryContextInjector(self.retriever)
        with self.assertRaises(ValueError):
            injector.build_context("   ")

    def test_invalid_context_limit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RetrieverMemoryContextInjector(self.retriever, max_characters=0)


if __name__ == "__main__":
    unittest.main()
