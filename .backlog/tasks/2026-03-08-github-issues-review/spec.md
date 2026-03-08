# Specs: Revue Issues GitHub et Ameliorations

> **Tache**: 2026-03-08-github-issues-review
> **Date**: 2026-03-08
> **Origine**: Issues GitHub #1, #2, #3, #4 + analyse qualite

## Vue d'ensemble

Traiter les 4 issues GitHub ouvertes du projet jellyfin-collection:
- Corriger le bug critique #4 (type conversion errors dans jellyfin.py)
- Fermer les issues #2 et #3 deja resolues avec commentaires explicatifs
- Repondre a l'issue #1 (documentation) avec des exemples concrets
- Nettoyer les dependances inutiles (fastapi, uvicorn, aiohttp)
- Ajouter un .dockerignore manquant

## Scope

### S1 - Fix Issue #4: Type conversion errors dans jellyfin.py

**Probleme**: Les provider IDs Jellyfin peuvent contenir des slugs (ex: `73375-jack-ryan`) au lieu d'entiers purs. Les appels `int()` directs provoquent des `ValueError` qui crashent le preloading au demarrage.

**5 occurrences a corriger**:
- Ligne 108: `tmdb_id=int(provider_ids["Tmdb"])` dans `get_library_items()`
- Ligne 110: `tvdb_id=int(provider_ids["Tvdb"])` dans `get_library_items()`
- Ligne 166: `tmdb_id=int(provider_ids["Tmdb"])` dans `search_items()`
- Ligne 168: `tvdb_id=int(provider_ids["Tvdb"])` dans `search_items()`
- Ligne 231: `tmdb_id=int(item_tmdb_id)` dans `find_by_tmdb_id()`
- Ligne 233: `tvdb_id=int(provider_ids["Tvdb"])` dans `find_by_tmdb_id()`

**Solution**: Creer une fonction helper `_safe_int()` qui:
1. Accepte une string ou None
2. Tente `int(value)` directement
3. En cas de ValueError, extrait la partie numerique initiale via regex (`re.match(r'(\d+)', value)`)
4. Retourne None si aucun entier extractible

**Fichiers concernes**:
- `src/jfc/clients/jellyfin.py` - modifier (ajouter helper + remplacer 6 appels int())

### S2 - Fermer issues resolues (#2 et #3)

**Issue #2** (limite 10k items): La pagination jusqu'a 50k items est implementee dans `get_library_items()`. Commenter avec explication et fermer.

**Issue #3** (plex_search + TMDb pagination): Les deux problemes sont corriges. Commenter avec details et fermer.

**Note**: Cette tache necessite l'utilisation de `gh` CLI (GitHub CLI). Si non disponible, documenter les commentaires a poster manuellement.

**Actions**:
- `gh issue comment 2 --body "..."`
- `gh issue close 2`
- `gh issue comment 3 --body "..."`
- `gh issue close 3`

### S3 - Supprimer dependances inutiles

**Dependances a supprimer de `pyproject.toml`**:
- `fastapi>=0.109.0` - jamais importe dans le code
- `uvicorn[standard]>=0.27.0` - jamais importe dans le code
- `aiohttp>=3.9.0` - jamais importe, redondant avec httpx

**Impact**: Reduction significative de la taille de l'image Docker (~500MB).

**Fichiers concernes**:
- `pyproject.toml` - modifier (supprimer 3 lignes de dependances + commentaire section)

### S4 - Ajouter .dockerignore

**Probleme**: Sans .dockerignore, le build Docker copie des fichiers inutiles (logs, data, .git, .venv, caches Python).

**Fichier a creer**: `.dockerignore` avec exclusions:
```
.git/
.venv/
__pycache__/
*.pyc
.env
.env.*
logs/
data/
.backlog/
.mypy_cache/
.pytest_cache/
.ruff_cache/
htmlcov/
*.egg-info/
dist/
build/
node_modules/
.idea/
.vscode/
*.md
!README.md
```

**Fichiers concernes**:
- `.dockerignore` - creer

### S5 - Repondre a issue #1 (documentation franchises)

**Probleme**: L'utilisateur demande comment configurer des collections "Franchises/Universes" (MCU, Star Wars, etc.).

**Solution**: Commenter l'issue avec des exemples YAML concrets utilisant les builders supportes (`tmdb_list`, `trakt_list`, `mdblist_list`) pour creer des collections franchise.

**Exemple a fournir**:
```yaml
collections:
  Marvel Cinematic Universe:
    tmdb_list: 131292
    sync_mode: sync
    sort_title: "!040_MCU"
    schedule: weekly(sunday)

  Star Wars:
    trakt_list: https://trakt.tv/users/user/lists/star-wars
    sync_mode: sync
    schedule: monthly
```

**Actions**:
- `gh issue comment 1 --body "..."`

## Criteres d'acceptation

### S1 - Fix Issue #4
- [ ] Fonction `_safe_int()` ajoutee dans jellyfin.py
- [ ] Les 6 appels `int()` sur provider IDs remplaces par `_safe_int()`
- [ ] Les slugs type `73375-jack-ryan` sont correctement parses en `73375`
- [ ] Les valeurs non-numeriques retournent `None` sans crash
- [ ] Le code compile sans erreur

### S2 - Fermer issues resolues
- [ ] Issue #2 commentee avec explication technique (pagination 50k)
- [ ] Issue #2 fermee
- [ ] Issue #3 commentee avec explication technique (plex_search + TMDb pagination)
- [ ] Issue #3 fermee

### S3 - Supprimer dependances inutiles
- [ ] fastapi supprime de pyproject.toml
- [ ] uvicorn supprime de pyproject.toml
- [ ] aiohttp supprime de pyproject.toml
- [ ] Le projet s'installe correctement apres suppression

### S4 - Ajouter .dockerignore
- [ ] Fichier .dockerignore cree a la racine
- [ ] Exclut .git, .venv, logs, data, caches, IDE files

### S5 - Repondre a issue #1
- [ ] Commentaire poste sur issue #1 avec exemples YAML franchises
- [ ] Exemples utilisent les builders supportes (tmdb_list, trakt_list, mdblist_list)

## Fichiers concernes

| Fichier | Action | Scope |
|---------|--------|-------|
| `src/jfc/clients/jellyfin.py` | Modifier | S1 |
| `pyproject.toml` | Modifier | S3 |
| `.dockerignore` | Creer | S4 |

## Hors scope

- Ajout de tests unitaires (tache separee)
- Refactoring du cache MediaMatcher (thread-safety)
- CI/CD quality gates (linting, tests en CI)
- Retry logic / circuit breaker pour clients HTTP
- Bare except cleanup (8 occurrences)
- Documentation complete des franchises (guide dedie)
- Resource limits dans docker-compose
- Portainer compatibility fix
