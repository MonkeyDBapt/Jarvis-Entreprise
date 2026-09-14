import tempfile
import unittest
from pathlib import Path

from jarvis.core import Memory, MemoryType
from jarvis.memory import SQLiteMemoryStore
from jarvis.interfaces import MemoryStore


class MemoryStorageTests(unittest.TestCase):
    def test_sqlite_store_implements_storage_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteMemoryStore(Path(directory) / "memory.sqlite3")
            self.assertIsInstance(store, MemoryStore)
            store.close()

    def test_memory_round_trip_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteMemoryStore(Path(directory) / "memory.sqlite3")
            memory = Memory(
                id="memory-1",
                content="JARVIS storage test",
                memory_type=MemoryType.LONG_TERM,
                scope="test",
                metadata={"source": "unit-test", "priority": 2},
            )
            store.save(memory)
            restored = store.get("memory-1")

            self.assertEqual(restored, memory)
            self.assertEqual(store.count(), 1)
            store.close()

    def test_save_replaces_existing_memory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteMemoryStore(Path(directory) / "memory.sqlite3")
            store.save(Memory("memory-1", "first", MemoryType.SHORT_TERM))
            store.save(Memory("memory-1", "second", MemoryType.CONTEXTUAL))

            restored = store.get("memory-1")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.content, "second")
            self.assertEqual(restored.memory_type, MemoryType.CONTEXTUAL)
            self.assertEqual(store.count(), 1)
            store.close()

    def test_delete_and_missing_memory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteMemoryStore(Path(directory) / "memory.sqlite3")
            store.save(Memory("memory-1", "delete me", MemoryType.SHORT_TERM))

            self.assertTrue(store.delete("memory-1"))
            self.assertFalse(store.delete("memory-1"))
            self.assertIsNone(store.get("memory-1"))
            self.assertEqual(store.count(), 0)
            store.close()


if __name__ == "__main__":
    unittest.main()
