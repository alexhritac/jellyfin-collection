# Exploration GitHub Issues

## Issues Ouvertes (4)

### #4 - Preload libraries fails with type conversion errors during startup
- **Date**: 2026-02-22
- **Type**: Bug CRITIQUE
- **Description**: Erreurs de conversion de type au demarrage lors du preloading:
  1. TV Shows: `invalid literal for int() with base 10: '73375-jack-ryan'` - slug interprete comme entier
  2. Movies: erreur validation Pydantic sur `LibraryItem.library_name` - int passe au lieu de string
- **Resultat**: 0/2 collections traitees

### #3 - plex search and tmdb issues
- **Date**: 2026-02-13
- **Type**: Bug
- **Description**:
  1. plex_search ne fonctionne pas: "Source: Unknown", 0 items
  2. TMDb ne retourne que 20 resultats meme avec limit: 50 (pagination manquante)

### #2 - Loading library limited to 10,000 items
- **Date**: 2026-02-12
- **Type**: Bug/Feature
- **Description**: Chargement Jellyfin plafonne a 10,000 items. Utilisateurs avec >10k films ont un matching incomplet.

### #1 - Not understanding the layout
- **Date**: 2026-01-23
- **Type**: Question/Documentation
- **Description**: Demande de support pour collections "Franchises/Universes" (MCU, Star Wars). Besoin de meilleure doc.

## Issues Fermees Recemment
Aucune.
