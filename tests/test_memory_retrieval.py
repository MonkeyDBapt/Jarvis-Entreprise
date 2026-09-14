import tempfile
import unittest
from pathlib import Path

from jarvis.core import Memory, MemoryType
from jarvis.interfaces import MemoryRetriever
from jarvis.memory import SQLiteMemoryRetriever, SQLiteMemoryStore


class MemoryRetrievalTests(unittest.TestCase):
    def _store(self, directory: str) -> SQLiteMemoryStore:
        store = SQLiteMemoryStore(Path(directory) / "memory.sqlite3")
        store.save(Memory("m1", "Python automation for JARVIS", MemoryType.LONG_TERM, scope="jarvis"))
        store.save(Memory("m2", "Minecraft server configuration", MemoryType.CONTEXTUAL, scope="gaming"))
        store.save(Memory("m3", "JARVIS memory and Python tests", MemoryType.USER, scope="jarvis"))
        store.save(Memory("m4", "Unrelated note", MemoryType.SHORT_TERM, scope="other"))
        return store

    def test_sqlite_retriever_implements_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self._store(directory)
            retriever = SQLiteMemoryRetriever(Path(directory) / "memory.sqlite3")
            self.assertIsInstance(retriever, MemoryRetriever)
            self.assertEqual([r.memory.id for r in retriever.search("JARVIS Python")], ["m3", "m1"])
            retriever.close()
            store.close()

    def test_search_is_ranked_and_limited(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self._store(directory)
            retriever = SQLiteMemoryRetriever(Path(directory) / "memory.sqlite3")
            results = retriever.search("JARVIS", limit=1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].memory.id, "m1")
            self.assertGreater(results[0].score, 0)
            retriever.close()
            store.close()

    def test_search_supports_type_and_scope_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self._store(directory)
            retriever = SQLiteMemoryRetriever(Path(directory) / "memory.sqlite3")
            results = retriever.search("JARVIS", memory_type=MemoryType.USER, scope="jarvis")
            self.assertEqual([r.memory.id for r in results], ["m3"])
            retriever.close()
            store.close()

    def test_search_is_case_insensitive_and_returns_empty_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self._store(directory)
            retriever = SQLiteMemoryRetriever(Path(directory) / "memory.sqlite3")
            self.assertEqual([r.memory.id for r in retriever.search("python")], ["m3", "m1"])
            self.assertEqual(retriever.search("does-not-exist"), [])
            retriever.close()
            store.close()

    def test_invalid_query_and_limit_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self._store(directory)
            retriever = SQLiteMemoryRetriever(Path(directory) / "memory.sqlite3")
            with self.assertRaises(ValueError):
                retriever.search("   ")
            with self.assertRaises(ValueError):
                retriever.search("JARVIS", limit=0)
            retriever.close()
            store.close()


if __name__ == "__main__":
    unittest.main()
