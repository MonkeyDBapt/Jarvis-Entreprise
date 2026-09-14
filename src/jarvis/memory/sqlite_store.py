"""SQLite persistence backend for JARVIS Enterprise memory."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional, Union

from jarvis.core.memory import Memory, MemoryType
from jarvis.interfaces.memory_store import MemoryStore


class SQLiteMemoryStore(MemoryStore):
    """Persistent local memory store backed by SQLite.

    SQLite is used as the initial backend because it is built into Python,
    persistent, transactional, serverless, and easy to replace through the
    ``MemoryStore`` contract.
    """

    def __init__(self, path: Union[str, Path] = ".data/memory.sqlite3") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self.path))
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def save(self, memory: Memory) -> None:
        self._connection.execute(
            """
            INSERT INTO memories (id, content, memory_type, scope, metadata)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                content = excluded.content,
                memory_type = excluded.memory_type,
                scope = excluded.scope,
                metadata = excluded.metadata
            """,
            (
                memory.id,
                memory.content,
                memory.memory_type.value,
                memory.scope,
                json.dumps(memory.metadata, ensure_ascii=False, sort_keys=True),
            ),
        )
        self._connection.commit()

    def get(self, memory_id: str) -> Optional[Memory]:
        row = self._connection.execute(
            "SELECT id, content, memory_type, scope, metadata FROM memories WHERE id = ?",
            (memory_id,),
        ).fetchone()
        if row is None:
            return None
        return Memory(
            id=row["id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            scope=row["scope"],
            metadata=json.loads(row["metadata"]),
        )

    def delete(self, memory_id: str) -> bool:
        cursor = self._connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self._connection.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        row = self._connection.execute("SELECT COUNT(*) AS count FROM memories").fetchone()
        return int(row["count"])

    def close(self) -> None:
        self._connection.close()
