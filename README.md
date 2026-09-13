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
`JarvisOrchestrator` builds a Microsoft Agent Framework workflow whose `HermesExecutor` delegates execution to the isolated `HermesAdapter` through the JARVIS `AgentRuntime` contract.

### Phase 2 status

**Phase 2 — Socle technique: clôturée.**

The consolidated reference architecture is:

```text
JARVIS Enterprise
       │
       ▼
JarvisOrchestrator
       │
       ▼
Microsoft Agent Framework
       │
       ▼
AgentRuntime
       │
       ▼
HermesAdapter
       │
       ▼
Hermes
       │
       ▼
LLM
```

The detailed consolidation record is available in [`docs/phase-2-socle.md`](docs/phase-2-socle.md).

Current Phase 2 scope is intentionally minimal: MAF provides the orchestration boundary and workflow execution path, while Hermes provides the current operational runtime. Hierarchical multi-agent routing, governance, messaging/event infrastructure, higher-level interfaces, and additional specialized capabilities remain subsequent work.

### Phase 3 status

**3.1 — Modèle d'organisation: validée.**  
**3.2 — Modèle Agent: validée.**  
**3.3 — Registre des agents: validée.**

The agent registry is a JARVIS-owned index of declarative agent definitions. It provides stable-ID registration, lookup, presence checks, ordered listing, and removal while remaining independent from runtime execution, routing, permissions, governance, and messaging.

The repository includes unit tests for the organization hierarchy, agent model, registry, runtime interface, and MAF routing. GitHub Actions validates the package and test suite across Python 3.10, 3.11, 3.12, and 3.13.

Run the local test suite with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```
