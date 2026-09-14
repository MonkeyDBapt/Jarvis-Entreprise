import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jarvis.core.memory import Memory, MemoryType
from jarvis.memory.lifecycle import MemoryLifecycleManager, expiration_metadata
from jarvis.memory.sqlite_retriever import SQLiteMemoryRetriever
from jarvis.memory.sqlite_store import SQLiteMemoryStore
from jarvis.interfaces.memory_lifecycle import MemoryLifecycleState


class MemoryLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "memory.sqlite3"
        self.store = SQLiteMemoryStore(self.path)
        self.lifecycle = MemoryLifecycleManager(self.store)
        self.store.save(Memory(id="m1", content="JARVIS mémoire active", memory_type=MemoryType.LONG_TERM, scope="project"))
        self.store.save(Memory(id="m2", content="JARVIS mémoire archive", memory_type=MemoryType.LONG_TERM, scope="project"))
        self.lifecycle.archive("m2")

    def tearDown(self) -> None:
        self.store.close()
        self.tempdir.cleanup()

    def test_default_state_is_active(self) -> None:
        self.assertEqual(self.lifecycle.get_state("m1"), MemoryLifecycleState.ACTIVE)

    def test_archive_and_restore(self) -> None:
        self.assertEqual(self.lifecycle.get_state("m2"), MemoryLifecycleState.ARCHIVED)
        retriever = SQLiteMemoryRetriever(self.path)
        try:
            results = retriever.search("JARVIS mémoire")
            self.assertEqual([result.memory.id for result in results], ["m1"])
        finally:
            retriever.close()
        self.lifecycle.restore("m2")
        self.assertEqual(self.lifecycle.get_state("m2"), MemoryLifecycleState.ACTIVE)

    def test_expired_memory_is_not_retrieved(self) -> None:
        memory = self.store.get("m1")
        assert memory is not None
        memory.metadata.update(expiration_metadata(datetime.now(timezone.utc) - timedelta(seconds=1)))
        self.store.save(memory)
        retriever = SQLiteMemoryRetriever(self.path)
        try:
            self.assertEqual(retriever.search("JARVIS mémoire"), [])
        finally:
            retriever.close()

    def test_purge_expired_removes_expired_memory(self) -> None:
        self.assertTrue(self.lifecycle.expire("m1"))
        self.assertEqual(self.lifecycle.purge_expired(), 1)
        self.assertIsNone(self.store.get("m1"))

    def test_delete_is_permanent(self) -> None:
        self.assertTrue(self.lifecycle.delete("m2"))
        self.assertIsNone(self.store.get("m2"))

    def test_missing_memory_is_safe(self) -> None:
        self.assertIsNone(self.lifecycle.get_state("missing"))
        self.assertFalse(self.lifecycle.archive("missing"))


if __name__ == "__main__":
    unittest.main()
