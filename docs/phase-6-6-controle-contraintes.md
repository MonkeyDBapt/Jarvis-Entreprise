# Phase 6.6 — Contrôle / contraintes

## Statut

**Validée.**

## Objectif

Ajouter une frontière provider-neutral de **contrôle des modèles** après l'expression de l'intention et avant l'exécution.

Les contraintes de 6.6 sont des règles dures : elles ne sont ni des préférences, ni des métriques inventées, ni des appels provider.

## Contrat

`ModelControlConstraints` permet de définir :

- les providers autorisés ;
- les types de modèles autorisés ;
- une limite maximale de contexte ;
- une limite maximale de sortie ;
- une température maximale ;
- des métadonnées de politique non exécutables.

Le contrat est immuable et valide ses propres paramètres.

## Intégration

`ModelRouter.select()` accepte désormais des contraintes optionnelles.

Le traitement est :

```text
ModelUsageRequest
       │
       ▼
ModelSelectionRequest
       │
       ├──────────────► ModelControlConstraints
       │                         │
       ▼                         ▼
                  ModelRouter / contrôle
                         │
                         ▼
                    ModelRegistry
```

Les contraintes explicites sont vérifiées avant le routage. Les candidats incompatibles sont écartés. Un modèle explicitement demandé est refusé s'il viole une contrainte.

## Règles

1. Une contrainte de contrôle est prioritaire sur une préférence de sélection.
2. Une contrainte incompatible avec une demande explicite provoque un refus déterministe.
3. Le routeur ne contourne jamais une contrainte pour trouver un modèle.
4. Les contraintes de capacité de contexte/sortie s'appuient uniquement sur les valeurs déclarées dans `ModelConfiguration`.
5. Aucune information provider-specific non déclarée n'est inventée.
6. Les credentials, quotas réels, prix réels, latence réelle et disponibilité restent hors périmètre.
7. L'exécution du modèle reste hors de 6.6.

## Validation

Les tests couvrent :

- filtrage des candidats par contraintes ;
- rejet d'un modèle explicitement demandé mais non conforme ;
- rejet d'une contrainte provider contradictoire ;
- immutabilité des métadonnées de contrôle.

La validation finale est exécutée par la CI GitHub sur Python 3.10, 3.11, 3.12 et 3.13.

Aucun secret ou credential réel n'est ajouté au dépôt.
