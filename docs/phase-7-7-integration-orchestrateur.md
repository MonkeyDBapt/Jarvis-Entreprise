# Phase 7.7 — Intégration orchestrateur

## Statut

**Validée.**

## Objectif

Relier la couche de communication de Phase 7 à `JarvisOrchestrator` sans contourner les contrats déjà établis pour l'orchestration, la sécurité et les transports.

## Intégration retenue

`JarvisOrchestrator` accepte désormais un `CommunicationRouter` optionnel. La méthode `run_and_reply()` :

1. exécute la requête par le chemin d'orchestration existant ;
2. construit un `CommunicationMessage` de type `response` ;
3. conserve les identifiants de session et de tâche ainsi que la corrélation éventuelle ;
4. remet la réponse au `CommunicationRouter` ;
5. laisse donc le routage, le transport et l'autorisation de communication aux frontières de Phase 7.

Architecture :

```text
OrchestrationRequest
       │
       ▼
JarvisOrchestrator
       │
       ├── Organization / Agents
       ├── Capabilities / Security
       ├── Memory
       ├── Intelligence
       │
       ▼
Microsoft Agent Framework
       │
       ▼
AgentRuntime / Hermes
       │
       ▼
response
       │
       ▼
CommunicationRouter
       │
       ├── SecurityController
       └── MessageDelivery / Transport
```

## Limites conservées

- Le routeur de communication reste indépendant du runtime agent.
- Le transport concret n'est pas exposé à l'orchestrateur.
- La sécurité de communication n'est pas contournée : `CommunicationRouter` continue d'autoriser ou de refuser l'envoi.
- `run()` conserve son comportement historique lorsqu'aucun routeur de communication n'est configuré.
- Aucun broker distribué, retry, persistance ou protocole externe n'est ajouté à cette étape.

## Validation

Tests dédiés :

- réponse d'orchestration routée via `CommunicationRouter` ;
- conservation de la corrélation/session/tâche ;
- échec explicite si l'intégration communication est demandée sans routeur ;
- refus de la réponse lorsque `SecurityController` n'autorise pas l'envoi.

La validation CI doit couvrir Python 3.10 à 3.13 et la suite de tests complète.
