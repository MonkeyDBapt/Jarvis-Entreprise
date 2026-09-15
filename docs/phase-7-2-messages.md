# Phase 7.2 — Messages

## Statut

**Validée.**

## Objectif

Fournir une frontière de communication point-à-point indépendante du transport concret, compatible avec l'architecture hybride retenue pour JARVIS Enterprise.

## Périmètre

- `CommunicationMessage` constitue l'enveloppe de message définie en 7.1.
- `MessageDelivery` définit le contrat de livraison.
- `InMemoryMessageDelivery` fournit l'implémentation locale de référence.
- Un destinataire est identifié par `recipient_id`.
- Un seul handler actif est associé à un identifiant destinataire.
- La livraison est synchrone, déterministe et sans dépendance à un broker externe.
- Les erreurs de livraison sont explicites via `MessageDeliveryError`.
- L'enveloppe conserve les identifiants de corrélation, de causalité, de session et de tâche définis en 7.1.

## Architecture

```text
Component A
    │
    │ CommunicationMessage
    ▼
MessageDelivery
    │
    ▼
InMemoryMessageDelivery
    │
    ▼
Handler du destinataire
    │
    ▼
Component B
```

La frontière `MessageDelivery` permet de remplacer ultérieurement l'implémentation locale par un transport distribué sans modifier le modèle de message ni les composants producteurs/consommateurs.

## Contrôles validés

- livraison au destinataire enregistré ;
- refus d'une livraison sans destinataire ;
- refus d'un destinataire sans handler ;
- refus des doubles enregistrements ;
- désenregistrement effectif ;
- validation des identifiants et handlers.

## Hors périmètre

Les événements, canaux/transport concrets, communication asynchrone distribuée, persistance, retry, dead-letter et intégration complète à l'orchestrateur restent traités dans les étapes ultérieures de la Phase 7.
