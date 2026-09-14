"""Deterministic textual retrieval over the SQLite memory backend."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from jarvis.core.memory import Memory, MemoryType
from jarvis.interfaces.memory_retriever import MemoryRetriever, MemorySearchResult
from jarvis.interfaces.memory_lifecycle import MemoryLifecycleState
from jarvis.memory.lifecycle import is_expired

_TOKEN_RE = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


class SQLiteMemoryRetriever(MemoryRetriever):
    """Retrieve memories using local lexical matching and deterministic ranking."""

    def __init__(self, path: Union[str, Path] = ".data/memory.sqlite3") -> None:
        self.path = Path(path)
        self._connection = sqlite3.connect(str(self.path))
        self._connection.row_factory = sqlite3.Row

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[str] = None,
    ) -> list[MemorySearchResult]:
        if not query or not query.strip():
            raise ValueError("La requête de recherche ne peut pas être vide.")
        if limit < 1:
            raise ValueError("La limite de résultats doit être supérieure à zéro.")

        tokens = [token.casefold() for token in _TOKEN_RE.findall(query)]
        if not tokens:
            return []

        clauses: list[str] = []
        parameters: list[str] = []
        if memory_type is not None:
            clauses.append("memory_type = ?")
            parameters.append(memory_type.value)
        if scope is not None:
            clauses.append("scope = ?")
            parameters.append(scope)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"SELECT id, content, memory_type, scope, metadata FROM memories {where}",
            parameters,
        ).fetchall()

        results: list[MemorySearchResult] = []
        now = datetime.now(timezone.utc)
        for row in rows:
            metadata = json.loads(row["metadata"])
            state = metadata.get("lifecycle_state", MemoryLifecycleState.ACTIVE.value)
            if state != MemoryLifecycleState.ACTIVE.value or is_expired(metadata, now=now):
                continue

            content_tokens = [token.casefold() for token in _TOKEN_RE.findall(row["content"])]
            content_set = set(content_tokens)
            matched = sum(content_tokens.count(token) for token in tokens)
            unique_matches = sum(token in content_set for token in tokens)
            phrase_bonus = 1.0 if query.strip().casefold() in row["content"].casefold() else 0.0
            score = float(matched) + (0.5 * unique_matches) + phrase_bonus
            if score <= 0:
                continue

            memory = Memory(
                id=row["id"],
                content=row["content"],
                memory_type=MemoryType(row["memory_type"]),
                scope=row["scope"],
                metadata=metadata,
            )
            results.append(MemorySearchResult(memory=memory, score=score))

        results.sort(key=lambda result: (-result.score, result.memory.id))
        return results[:limit]

    def close(self) -> None:
        self._connection.close()
