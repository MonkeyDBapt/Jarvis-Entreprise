#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT/.runtime"
HERMES_DIR="$RUNTIME_DIR/hermes-agent"

command -v git >/dev/null 2>&1 || { echo "Erreur: git est requis."; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "Erreur: uv est requis. Installe-le avant de relancer ce script."; exit 1; }

mkdir -p "$RUNTIME_DIR"

if [ -d "$HERMES_DIR/.git" ]; then
  echo "Hermes déjà présent: $HERMES_DIR"
else
  git clone https://github.com/NousResearch/hermes-agent.git "$HERMES_DIR"
fi

cd "$HERMES_DIR"
uv sync

PYTHON_BIN="$(uv run python -c 'import sys; print(sys.executable)')"
"$PYTHON_BIN" -c 'from run_agent import AIAgent; print("Hermes import OK")'

echo
printf 'Hermes installé et vérifié dans: %s\n' "$HERMES_DIR"
printf 'Python Hermes: %s\n' "$PYTHON_BIN"
printf 'Version Hermes: '
uv run python -c 'from importlib.metadata import version; print(version("hermes-agent"))'
