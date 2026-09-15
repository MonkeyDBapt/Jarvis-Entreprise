# Phase 8.7 — Intégration orchestrateur

## Objectif

Faire de l'orchestrateur JARVIS le point de passage entre les permissions, l'autonomie, le contrôle/supervision et l'exécution MAF.

## Intégration

`JarvisOrchestrator` expose désormais :

- un registre d'attributions de permissions optionnel ;
- un `AuthorizationEvaluator` ;
- un `ControlEvaluator` ;
- `evaluate_control(...)` pour produire une décision déterministe ;
- l'intégration de cette décision dans `run(...)` avant la résolution de l'agent et l'entrée dans le workflow MAF.

Le chemin de contrôle est :

```text
OrchestrationRequest
        ↓
AuthorizationEvaluator
        ↓
ControlEvaluator
        ↓
Permission
   ├── denied → arrêt
   └── allowed
         ↓
      autonomie
      ├── approval/supervision → arrêt avant exécution
      └── autonomous → MAF
                         ↓
                      AgentRuntime
```

## Règles

1. Une autorisation refusée est terminale.
2. Une autonomie insuffisante ne devient jamais une autorisation implicite.
3. Une requête de contrôle partielle est rejetée.
4. Les requêtes existantes sans paramètres de contrôle restent compatibles tant que la couche de permissions n'est pas activée pour cette requête.
5. L'exécution ne franchit la frontière MAF que lorsque le contrôle demandé autorise l'autonomie nécessaire.

## Validation

Les tests d'intégration couvrent :

- autorisation + autonomie autorisant l'exécution autonome ;
- permission absente ;
- autonomie supervisée bloquant l'exécution ;
- requête de contrôle incomplète.

**Statut : 8.7 validée.**
