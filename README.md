# Jarvis-Entreprise

## Runtime

JARVIS Enterprise keeps external runtimes isolated from the main Python environment.

### Hermes Agent

Hermes is integrated as the operational agent runtime through `jarvis.runtime.HermesAdapter`.
Its source checkout and dependencies stay isolated under `.runtime/hermes-agent/` and are not vendored into the JARVIS package.

Setup in a Codespace:

```bash
git pull
bash scripts/setup_hermes.sh
```

The setup script clones the official Hermes repository, runs its supported `uv sync` environment setup, and verifies that `AIAgent` can be imported. Hermes currently requires Python `>=3.11,<3.14`; this is intentionally kept separate from JARVIS's main environment.

After setup, API/provider credentials must be configured according to Hermes' own configuration rules before executing model-backed tasks. Secrets must not be committed to Git.

### Microsoft Agent Framework

The JARVIS orchestration boundary is implemented with `agent-framework-core==1.18.0`.
`JarvisOrchestrator` builds a Microsoft Agent Framework workflow whose `HermesExecutor` delegates execution to the isolated `HermesAdapter`.

Current Phase 2 scope is intentionally minimal: MAF provides the orchestration boundary and workflow execution path; hierarchical multi-agent routing, governance, messaging/event infrastructure, and higher-level interfaces remain subsequent Phase 2 work.

The repository includes unit tests for request routing and a GitHub Actions test workflow. A successful CI run validates the package installation and MAF API imports/tests; a model-backed Hermes run still requires the local Hermes runtime and provider credentials.

Run the local test suite with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```
