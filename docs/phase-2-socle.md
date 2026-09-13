# Phase 2 — Socle technique

## Statut

**Phase 2 clôturée — 2.8 Consolidation validée.**

## Périmètre consolidé

| Étape | Statut |
|---|---|
| 2.1 — Définition du socle | ✅ Terminée |
| 2.2 — Sélection / validation des briques | ✅ Terminée |
| 2.3 — Environnement technique | ✅ Terminé |
| 2.4 — Intégration Hermes | ✅ Terminée |
| 2.5 — Intégration Microsoft Agent Framework | ✅ Terminée |
| 2.6 — Interfaces / adaptateurs | ✅ Terminée |
| 2.7 — Validation globale | ✅ Validée |
| 2.8 — Consolidation / clôture | ✅ Validée |

## Architecture de référence à la clôture

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

## Frontières validées

- `JarvisOrchestrator` constitue la frontière d'orchestration JARVIS.
- Microsoft Agent Framework fournit l'exécution du workflow d'orchestration.
- `AgentRuntime` constitue le contrat JARVIS stable entre l'orchestrateur et un runtime d'agent.
- `HermesAdapter` est l'implémentation actuelle de ce contrat.
- Hermes reste isolé de l'environnement Python principal de JARVIS.
- Le remplacement futur du runtime ne nécessite pas de modifier le contrat d'orchestration.

## Validation et CI

La CI de validation est centralisée dans `.github/workflows/tests.yml` et couvre Python 3.10, 3.11, 3.12 et 3.13. La découverte des tests est explicitement exécutée depuis `GITHUB_WORKSPACE` avec le motif `test_*.py`.

La présence de la configuration CI constitue une garantie de validation automatisée sur les commits concernés. Une exécution CI fraîche doit toutefois être considérée comme la preuve d'exécution pour un commit donné ; l'absence d'un run accessible ne doit pas être transformée en succès supposé.

## Hors périmètre à la clôture

La clôture de la Phase 2 ne signifie pas que JARVIS Enterprise est fonctionnellement complet. Restent volontairement hors de ce socle :

- hiérarchie Pôles → Équipes → Agents ;
- gouvernance et permissions de niveau supérieur ;
- messaging / événements distribués ;
- mémoire JARVIS de niveau supérieur ;
- interfaces utilisateur ;
- capacités et outils spécialisés supplémentaires ;
- intégration de nouveaux runtimes ou briques optionnelles.

Ces éléments appartiennent aux phases de construction ultérieures et ne doivent pas être ajoutés rétroactivement au socle sans nouvelle décision d'architecture.

## Règle de stabilité

À partir de la clôture 2.8, MAF, Hermes et la frontière `AgentRuntime` sont considérés comme **socle stable de référence**. Toute modification future doit être motivée par un besoin de phase ultérieure et accompagnée d'une nouvelle validation adaptée.
