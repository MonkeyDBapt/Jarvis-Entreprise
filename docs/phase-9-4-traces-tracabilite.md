# Phase 9.4 — Traces / traçabilité

## Statut

**Validée / consolidée.**

## Objectif

Fournir à JARVIS Enterprise un contrat provider-independent permettant de reconstruire la chaîne causale d'une opération : une trace possède une identité stable, les opérations sont représentées par des spans, et les relations parent/enfant permettent de suivre le chemin d'exécution sans imposer un backend de tracing.

## Modèle retenu

```text
TraceContext
   │
   ├── trace_id
   ├── span_id
   └── parent_span_id
        │
        ▼
     TraceSpan
        │
        ├── operation
        ├── component
        ├── started_at / ended_at
        ├── status
        ├── attributes
        └── events
        │
        ▼
   TraceRecorder
```

### Identité et causalité

- `trace_id` identifie une chaîne complète d'exécution ;
- `span_id` identifie une opération dans cette chaîne ;
- `parent_span_id` permet de reconstruire la relation causale ;
- un contexte enfant conserve le même `trace_id` et crée un nouveau `span_id`.

### Statuts

- `unset` : aucun résultat final déclaré ;
- `ok` : opération terminée avec succès ;
- `error` : opération terminée avec erreur.

## Principes

- contrats indépendants d'un fournisseur ;
- identifiants générés localement lorsque nécessaires ;
- horodatages timezone-aware en UTC lors de la sérialisation ;
- durée calculable lorsqu'une fin est connue ;
- attributs et événements extensibles ;
- enregistrement thread-safe ;
- filtrage d'une trace par `trace_id` ;
- aucune dépendance à OpenTelemetry ou à une plateforme externe.

## Garanties

- les identifiants obligatoires ne peuvent pas être vides ;
- une opération et un composant sont obligatoires ;
- une fin ne peut pas précéder le début ;
- les événements vides sont rejetés ;
- la hiérarchie parent/enfant conserve l'identité de la trace ;
- les traces peuvent être récupérées sans imposer de persistance externe.

## Articulation avec les étapes précédentes

```text
Phase 9.1 — Vérification
        │
Phase 9.2 — Logs
        │
Phase 9.3 — Métriques / indicateurs
        │
Phase 9.4 — Traces / traçabilité  ← cette étape
        │
        ▼
Phase 9.5 — Validation / consolidation
```

Les logs restent destinés aux événements textuels structurés, les métriques aux mesures agrégées, et les traces à la reconstruction causale des opérations. Ces trois mécanismes restent séparés tout en pouvant partager les mêmes identifiants de corrélation lors d'une future intégration.

## Hors périmètre

La persistance longue durée, l'export OpenTelemetry, les collectors, les dashboards, le stockage distribué, l'analyse avancée et le tracing réseau externe restent hors périmètre de cette étape.

## Validation

`tests/test_observability_tracing.py` couvre :

- création et propagation de contexte ;
- relation parent/enfant ;
- calcul de durée ;
- sérialisation ;
- filtrage par trace ;
- rejet des données structurellement invalides.

La CI existante reste le mécanisme de validation automatique du dépôt.
