#!/usr/bin/env python3
"""Small process boundary between JARVIS and the isolated Hermes runtime."""

from __future__ import annotations

import json
import sys

from run_agent import AIAgent


def main() -> int:
    request = json.load(sys.stdin)
    agent = AIAgent(
        model=request.get("model", ""),
        quiet_mode=True,
        session_id=request.get("session_id"),
        max_iterations=request.get("max_iterations", 20),
    )
    result = agent.run_conversation(
        user_message=request["message"],
        task_id=request.get("task_id"),
    )
    json.dump(
        {
            "final_response": result.get("final_response", ""),
            "messages": result.get("messages", []),
        },
        sys.stdout,
        ensure_ascii=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
