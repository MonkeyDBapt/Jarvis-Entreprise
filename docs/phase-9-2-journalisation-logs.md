# Phase 9.2 — Journalisation / logs

## Statut

**Validée / consolidée.**

## Objectif

Fournir à JARVIS Enterprise un contrat de journalisation structuré, indépendant du backend, permettant de tracer les événements utiles à la vérification et à l'observabilité sans mélanger journalisation, persistance ou métriques.

## Modèle retenu

```text
StructuredLogger
      │
      ▼
   LogEntry
      │
      ├── timestamp
      ├── level
      ├── message
      ├── component
      ├── event
      ├── correlation_id
      ├── agent_id
      ├── task_id
      └── metadata
```

### Niveaux

- `debug`
- `info`
- `warning`
- `error`
- `critical`

### Principes

- format structuré JSON ;
- horodatage UTC ;
- identifiants de corrélation, agent et tâche lorsque disponibles ;
- métadonnées extensibles ;
- backend fondé sur le module standard Python `logging` ;
- aucune dépendance de fournisseur ajoutée ;
- les secrets et champs d'authentification courants sont automatiquement masqués ;
- la journalisation ne constitue pas une persistance durable ni un système de métriques.

## Garanties

- une entrée possède toujours un message et un composant non vides ;
- le niveau est explicite ;
- les données sensibles connues (`token`, `api_key`, `authorization`, `password`, etc.) sont redigées ;
- les entrées sont sérialisables en une ligne JSON ;
- le contrat reste utilisable indépendamment de la destination finale des logs.

## Frontières avec les étapes suivantes

```text
Phase 9.1
Modèle de vérification
       │
       ├── Phase 9.2 : journalisation / logs       ← cette étape
       ├── Phase suivante : exécution / contrôles
       ├── Phase suivante : traces / métriques
       └── Phase suivante : validation globale
```

La collecte, la rotation, l'expédition externe, la recherche centralisée, les métriques et le tracing distribué restent hors périmètre.

## Validation

`tests/test_observability_logging.py` couvre :

- sérialisation structurée ;
- présence des champs de contexte ;
- masquage des données sensibles ;
- émission via `logging` ;
- validation des champs d'identité.

La CI existante du dépôt reste le mécanisme de validation automatique.
