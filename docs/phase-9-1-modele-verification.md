# Phase 9.1 — Modèle de vérification

## Statut

**Validée / consolidée.**

## Objectif

Définir un contrat stable permettant à JARVIS Enterprise de représenter une vérification, son résultat, son niveau de gravité et ses éléments de preuve, sans mélanger le modèle avec l'exécution, la persistance ou l'observabilité.

## Modèle retenu

```text
VerificationReport
       │
       ├── id
       ├── scope
       ├── metadata
       │
       └── VerificationCheck[*]
              │
              ├── id
              ├── name
              ├── target
              ├── category
              ├── status
              ├── severity
              ├── expected
              ├── observed
              ├── evidence
              └── metadata
```

### Statuts

- `passed` — le contrôle est validé ;
- `failed` — le contrôle est en échec ;
- `inconclusive` — les éléments disponibles ne permettent pas de conclure ;
- `skipped` — le contrôle n'a pas été exécuté.

Une vérification `inconclusive` ne peut pas être considérée comme réussie.

### Gravité

- `info` — information ;
- `warning` — anomalie non bloquante ;
- `error` — erreur significative ;
- `critical` — erreur critique.

La gravité décrit l'impact du constat et ne remplace pas son statut.

## Garanties

- Les identifiants d'un rapport sont stables et non vides.
- Les contrôles d'un rapport possèdent des identifiants uniques.
- Le résultat agrégé ne masque jamais un échec.
- Un résultat inconclusif reste inconclusif.
- Un rapport vide ou entièrement ignoré n'est pas considéré comme réussi.
- Les preuves sont représentées explicitement mais leur collecte reste hors périmètre de 9.1.
- Le modèle ne déclenche aucune vérification et n'impose aucun backend d'observabilité.

## Frontières avec les phases suivantes

```text
Phase 9.1
Modèle de vérification
       │
       ├── Phase suivante : exécution / contrôles concrets
       ├── Phase suivante : observabilité / traces / métriques
       └── Phase suivante : validation globale / consolidation
```

Le modèle est volontairement indépendant des composants des phases 1 à 8. Il peut donc vérifier l'organisation, les capacités, la mémoire, l'intelligence, la communication, les permissions, l'orchestrateur ou le runtime sans couplage direct.

## Validation

Tests dédiés dans `tests/test_verification_model.py` couvrant :

- rapport entièrement réussi ;
- échec terminal du rapport ;
- résultat inconclusif ;
- unicité des identifiants ;
- validation des champs d'identité.

La CI existante reste le mécanisme de validation automatique du dépôt et conserve sa matrice Python 3.10 à 3.13.
