# Phase 7.6 — Contrôle / sécurité

## Objectif

Ajouter une frontière de contrôle de sécurité au routage de communication afin qu'un composant ne puisse pas envoyer un message ou publier un événement sans autorisation explicite lorsque le contrôle de sécurité est activé.

## Contrat retenu

La communication réutilise le `SecurityController` JARVIS établi en Phase 4.

- message : `sender_id` est le sujet de sécurité ; l'action est `send` ; la ressource est `communication:<recipient_id>` ;
- événement : `source_id` est le sujet de sécurité ; l'action est `publish` ; la ressource est `event:<event_type>`.

La politique reste en **default deny** lorsqu'un `SecurityController` est fourni : l'absence d'autorisation explicite provoque `PermissionError`.

## Position dans le flux

L'autorisation est évaluée par `CommunicationRouter` **avant** le handler direct, la livraison de message, la publication d'événement ou le transport concret.

```text
CommunicationMessage / CommunicationEvent
                │
                ▼
       CommunicationRouter
                │
                ▼
       SecurityController
          │           │
       deny          allow
          │           │
    PermissionError  ▼
                livraison / transport
```

Ainsi, un refus de sécurité ne doit produire aucune livraison secondaire.

## Compatibilité

Le contrôle est injecté dans `CommunicationRouter` et reste optionnel pour préserver les chemins historiques des phases précédentes lorsqu'aucune politique de sécurité n'est fournie.

Les méthodes `can_route_message()` et `can_route_event()` permettent une vérification sans exécution.

## Règles

- aucune autorisation implicite lorsqu'un contrôleur est configuré ;
- l'autorisation est vérifiée avant toute livraison ou publication ;
- `direct`, `message` et `event` restent soumis à la même frontière de contrôle ;
- la sécurité ne dépend d'aucun transport concret ;
- les permissions existantes peuvent être révoquées sans modifier le routeur ;
- les secrets, credentials et données d'authentification ne font pas partie des objets de communication ni des règles de ce niveau.

## Validation

`tests/test_communication_security.py` couvre :

- refus d'un message non autorisé avant livraison ;
- autorisation d'un message explicitement permis ;
- refus d'un événement non autorisé avant publication ;
- autorisation d'un événement explicitement permis ;
- effet de la révocation d'une permission ;
- vérification préalable via `can_route_message()` et `can_route_event()`.

## Limites volontairement conservées

Cette étape ne définit pas encore :

- authentification réseau ;
- chiffrement ;
- gestion de secrets ;
- rôles complexes ou RBAC complet ;
- politiques temporelles ;
- quotas ;
- audit spécialisé ;
- sécurité distribuée ;
- gestion des identités externes.

Ces responsabilités pourront être ajoutées derrière les frontières existantes dans des phases dédiées.
