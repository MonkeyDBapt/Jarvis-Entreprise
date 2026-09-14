"""Memory lifecycle and retention control for JARVIS Enterprise."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from jarvis.interfaces.memory_lifecycle import MemoryLifecycle, MemoryLifecycleState
from jarvis.interfaces.memory_store import MemoryStore

_STATE_KEY = "lifecycle_state"
_EXPIRES_AT_KEY = "expires_at"


class MemoryLifecycleManager(MemoryLifecycle):
    """Control memory state and expiration through the ``MemoryStore`` contract.

    Lifecycle metadata is stored with the memory so the persistence backend
    remains unchanged and replaceable.
    """

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def get_state(self, memory_id: str) -> Optional[MemoryLifecycleState]:
        memory = self.store.get(memory_id)
        if memory is None:
            return None
        state = memory.metadata.get(_STATE_KEY, MemoryLifecycleState.ACTIVE.value)
        try:
            return MemoryLifecycleState(state)
        except ValueError as exc:
            raise ValueError(f"État de cycle de vie invalide pour la mémoire {memory_id!r}.") from exc

    def _set_state(self, memory_id: str, state: MemoryLifecycleState) -> bool:
        memory = self.store.get(memory_id)
        if memory is None:
            return False
        memory.metadata[_STATE_KEY] = state.value
        self.store.save(memory)
        return True

    def activate(self, memory_id: str) -> bool:
        return self._set_state(memory_id, MemoryLifecycleState.ACTIVE)

    def archive(self, memory_id: str) -> bool:
        return self._set_state(memory_id, MemoryLifecycleState.ARCHIVED)

    def restore(self, memory_id: str) -> bool:
        return self._set_state(memory_id, MemoryLifecycleState.ACTIVE)

    def expire(self, memory_id: str) -> bool:
        return self._set_state(memory_id, MemoryLifecycleState.EXPIRED)

    def delete(self, memory_id: str) -> bool:
        return self.store.delete(memory_id)

    def purge_expired(self) -> int:
        # The stable MemoryStore contract intentionally exposes no listing API.
        # This implementation uses the SQLite backend's explicit purge hook
        # when available; other stores can provide the same behavior later.
        purge = getattr(self.store, "purge_expired", None)
        if callable(purge):
            return int(purge())
        return 0


def expiration_metadata(expires_at: datetime) -> dict[str, str]:
    """Return normalized lifecycle metadata for a future expiration instant."""
    if expires_at.tzinfo is None:
        raise ValueError("La date d'expiration doit être timezone-aware.")
    return {_EXPIRES_AT_KEY: expires_at.astimezone(timezone.utc).isoformat()}


def is_expired(metadata: dict[str, object], *, now: Optional[datetime] = None) -> bool:
    """Return whether lifecycle metadata has reached its expiration instant."""
    raw = metadata.get(_EXPIRES_AT_KEY)
    if not isinstance(raw, str) or not raw:
        return False
    try:
        expires_at = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError("Date d'expiration de mémoire invalide.") from exc
    if expires_at.tzinfo is None:
        raise ValueError("La date d'expiration doit être timezone-aware.")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("La date de référence doit être timezone-aware.")
    return current >= expires_at
