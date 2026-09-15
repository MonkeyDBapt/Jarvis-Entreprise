# Phase 9.5 — État / santé système

## Statut

**Validée / consolidée.**

## Objectif

Fournir à JARVIS Enterprise un contrat provider-independent permettant de représenter l'état de santé des composants et d'obtenir un état agrégé du système sans imposer un backend d'infrastructure.

## Modèle retenu

```text
HealthCheck
    │
    ▼
HealthCheckResult
    │
    ├── status
    ├── component
    ├── message
    ├── details
    └── critical
    │
    ▼
HealthRegistry
    │
    ▼
SystemHealth
```

### États

- `healthy` : le contrôle observé est opérationnel ;
- `degraded` : le système ou un composant reste utilisable avec une dégradation ;
- `unhealthy` : une défaillance est observée ;
- `unknown` : aucun état exploitable n'est encore disponible.

### Agrégation

- aucun résultat → `unknown` ;
- une défaillance critique → `unhealthy` ;
- une défaillance non critique → `degraded` ;
- une dégradation → `degraded` ;
- un état `unknown` parmi des contrôles observés → `degraded` ;
- tous les contrôles observés sont sains → `healthy`.

## Principes

- contrats indépendants d'un fournisseur ;
- contrôles explicitement enregistrés ;
- cohérence entre définition et résultat vérifiée ;
- registre thread-safe ;
- résultats triés de manière déterministe ;
- exécution des contrôles fournie par une fonction d'évaluation, sans imposer de méthode d'infrastructure ;
- sérialisation disponible pour une future exposition par API, logs ou dashboard.

## Articulation avec les étapes précédentes

```text
Phase 9.1 — Vérification
        │
Phase 9.2 — Logs
        │
Phase 9.3 — Métriques / indicateurs
        │
Phase 9.4 — Traces / traçabilité
        │
Phase 9.5 — État / santé système  ← cette étape
        │
        ▼
Phase 9 — consolidation
```

La santé système complète les mécanismes précédents : les vérifications produisent des contrôles, les logs décrivent les événements, les métriques mesurent les comportements, les traces reconstruisent les chaînes causales et l'état de santé fournit une vue agrégée de l'état opérationnel observé.

## Hors périmètre

Les probes réseau concrètes, endpoints HTTP de healthcheck, orchestration Kubernetes, supervision externe, alerting, dashboards, stockage distribué et politiques de remédiation automatique restent hors périmètre.

## Validation

`tests/test_observability_health.py` couvre :

- état initial inconnu ;
- enregistrement et observation d'un contrôle ;
- agrégation saine ;
- défaillance critique ;
- défaillance non critique ;
- exécution déterministe de plusieurs contrôles ;
- rejet des résultats incompatibles avec les contrats enregistrés.

La CI existante reste le mécanisme de validation automatique du dépôt.
