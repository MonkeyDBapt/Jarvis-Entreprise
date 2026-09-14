# JARVIS Enterprise

### Phase 6 status

**Phase 6 — Modèles / intelligence : en cours.**

| Étape | Statut |
|---|---|
| 6.1 — Modèle d’intelligence | ✅ Validée |
| 6.2 — Registre des modèles | ✅ **Validée** |
| 6.3 — Configuration | ✅ **Validée** |
| 6.4 — Sélection / routage | ✅ **Validée** |
| 6.5 — Stratégies d’utilisation | ✅ **Validée** |

Phase 6.1 defines the provider-independent declarative `Model`, `ModelType`, and `ModelCapability` contracts. Phase 6.2 adds `ModelRegistry`, which centrally registers models by stable identifier, rejects duplicates, supports lookup and removal, and exposes a deterministic immutable registration view. Phase 6.3 adds the immutable provider-neutral `ModelConfiguration` boundary for endpoints, parameters, context/output limits, operational limits, secret references, and provider-specific configuration. Secrets themselves are never stored in the model configuration or committed to Git.

Phase 6.4 adds the provider-neutral `ModelSelectionRequest`, `ModelSelectionResult`, and `ModelRouter` contracts. Selection is deterministic: an explicit model id takes precedence, then requested capabilities, model type, provider, and registration order as a stable tie-breaker. Routing performs no provider execution or secret resolution; those concerns remain outside this step.

Phase 6.5 adds provider-neutral model usage strategies. `ModelUsageStrategy` expresses high-level intent (`balanced`, `fast`, `quality`, `economical`, `reasoning`) and `ModelUsageRequest` translates that intent plus explicit constraints into the existing `ModelSelectionRequest` contract. Strategy resolution performs no provider execution, secret resolution, or runtime optimization.

The detailed consolidation records are available in [`docs/phase-6-2-model-registry.md`](docs/phase-6-2-model-registry.md), [`docs/phase-6-3-configuration.md`](docs/phase-6-3-configuration.md), [`docs/phase-6-4-selection-routage.md`](docs/phase-6-4-selection-routage.md), and [`docs/phase-6-5-strategies-utilisation.md`](docs/phase-6-5-strategies-utilisation.md).

## Tests

Run the local test suite with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```
