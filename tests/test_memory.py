import unittest

from jarvis.core import Memory, MemoryType


class MemoryModelTests(unittest.TestCase):
    def test_memory_contains_declarative_properties(self) -> None:
        memory = Memory(
            "memory-1",
            "Le contexte de la tâche courante.",
            MemoryType.CONTEXTUAL,
            scope="session-1",
            metadata={"source": "task"},
        )

        self.assertEqual(memory.id, "memory-1")
        self.assertEqual(memory.content, "Le contexte de la tâche courante.")
        self.assertIs(memory.memory_type, MemoryType.CONTEXTUAL)
        self.assertEqual(memory.scope, "session-1")
        self.assertEqual(memory.metadata, {"source": "task"})

    def test_memory_types_are_explicit(self) -> None:
        self.assertEqual(MemoryType.SHORT_TERM.value, "short_term")
        self.assertEqual(MemoryType.LONG_TERM.value, "long_term")
        self.assertEqual(MemoryType.CONTEXTUAL.value, "contextual")

    def test_memory_rejects_empty_identity_or_content(self) -> None:
        with self.assertRaises(ValueError):
            Memory("", "content", MemoryType.SHORT_TERM)

        with self.assertRaises(ValueError):
            Memory("memory-1", "", MemoryType.SHORT_TERM)

    def test_model_does_not_define_storage_or_retrieval(self) -> None:
        memory = Memory("memory-1", "content", MemoryType.LONG_TERM)

        self.assertFalse(hasattr(memory, "save"))
        self.assertFalse(hasattr(memory, "retrieve"))
        self.assertFalse(hasattr(memory, "delete"))


if __name__ == "__main__":
    unittest.main()
