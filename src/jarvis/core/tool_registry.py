"""Registry for reusable JARVIS tools."""

from __future__ import annotations

from .tool import Tool


class ToolRegistry:
    """Central index of declarative tool definitions, independent from execution."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool under its stable identifier."""
        if tool.id in self._tools:
            raise ValueError(f"L'outil '{tool.id}' est déjà enregistré.")
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> Tool:
        """Return a registered tool or raise KeyError when unknown."""
        return self._tools[tool_id]

    def unregister(self, tool_id: str) -> Tool:
        """Remove and return a registered tool."""
        return self._tools.pop(tool_id)

    def contains(self, tool_id: str) -> bool:
        """Return whether a tool is registered."""
        return tool_id in self._tools

    def list_tools(self) -> list[Tool]:
        """Return registered tools in registration order."""
        return list(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)
