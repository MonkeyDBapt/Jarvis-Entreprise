#!/usr/bin/env python3
"""Small process boundary between JARVIS and the isolated Hermes runtime."""

from __future__ import annotations

import contextlib
import json
import sys

from run_agent import AIAgent


def main() -> int:
    request = json.load(sys.stdin)
    from hermes_cli.config import load_config_readonly

    config = load_config_readonly()
    model_config = config.get("model", {}) or {}

    agent_kwargs = {
        "quiet_mode": True,
        "session_id": request.get("session_id"),
        "max_iterations": request.get("max_iterations", 20),
        "model": request.get("model") or model_config.get("default", ""),
        "provider": model_config.get("provider"),
        "base_url": model_config.get("base_url"),
        "api_mode": model_config.get("api_mode"),
    }

    agent = AIAgent(**agent_kwargs)
    with contextlib.redirect_stdout(sys.stderr):
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
