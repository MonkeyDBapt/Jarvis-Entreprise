"""JARVIS adapter for the isolated Hermes Agent runtime."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class HermesAdapter:
    """Invoke Hermes without mixing its dependency environment with JARVIS."""

    def __init__(self, hermes_dir: str | Path | None = None, uv_executable: str = "uv") -> None:
        root = Path(__file__).resolve().parents[3]
        self.hermes_dir = Path(hermes_dir or root / ".runtime" / "hermes-agent").resolve()
        self.bridge = root / "scripts" / "hermes_bridge.py"
        self.uv_executable = uv_executable

    def chat(
        self,
        message: str,
        *,
        model: str = "",
        session_id: str | None = None,
        task_id: str | None = None,
        max_iterations: int = 20,
        timeout: float | None = None,
    ) -> str:
        if not (self.hermes_dir / "run_agent.py").is_file():
            raise RuntimeError(
                f"Hermes n'est pas installé dans {self.hermes_dir}. "
                "Exécutez: bash scripts/setup_hermes.sh"
            )
        if not self.bridge.is_file():
            raise RuntimeError(f"Pont Hermes introuvable: {self.bridge}")

        request: dict[str, Any] = {
            "message": message,
            "model": model,
            "session_id": session_id,
            "task_id": task_id,
            "max_iterations": max_iterations,
        }
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.hermes_dir) + os.pathsep + env.get("PYTHONPATH", "")

        completed = subprocess.run(
            [
                self.uv_executable,
                "run",
                "--project",
                str(self.hermes_dir),
                "python",
                str(self.bridge),
            ],
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=self.hermes_dir,
            env=env,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "Erreur Hermes inconnue"
            raise RuntimeError(f"Hermes a échoué ({completed.returncode}): {detail}")

        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Réponse Hermes invalide: sortie non JSON") from exc
        return str(result.get("final_response", ""))
