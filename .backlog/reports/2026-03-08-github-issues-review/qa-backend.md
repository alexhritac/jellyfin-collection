# QA Backend: github-issues-review (Iteration 1)

## Resume
- **Status**: ACCEPTE
- **Date**: 2026-03-08
- **Testeur**: QA-Tester Agent

---

## Tests Effectues

### Compilation / Syntaxe

```bash
$ python -m py_compile src/jfc/clients/jellyfin.py
# COMPILE OK - aucune erreur
```

- [x] jellyfin.py compile sans erreur
- [x] pyproject.toml valide (tomllib parse OK)

### S1 - Fix Issue #4: Type conversion errors

#### Fonction _safe_int()

- [x] Fonction `_safe_int()` presente a la ligne 18 de `jellyfin.py`
- [x] Import `re` present en ligne 5
- [x] Signature correcte: `_safe_int(value: str | None) -> int | None`
- [x] Gere None -> None
- [x] Gere chaine vide -> None
- [x] Gere entier pur "73375" -> 73375
- [x] Gere slug "73375-jack-ryan" -> 73375
- [x] Gere valeur non-numerique "abc" -> None
- [x] Gere entier natif 123 -> 123
- [x] Gere "0" -> 0 (edge case: falsy mais valide)

#### Remplacement des appels int()

| Emplacement | Ancien pattern | Nouveau pattern | Status |
|-------------|---------------|-----------------|--------|
| L124 (get_library_items, Tmdb) | `int(provider_ids["Tmdb"])` | `_safe_int(provider_ids.get("Tmdb"))` | OK |
| L126 (get_library_items, Tvdb) | `int(provider_ids["Tvdb"])` | `_safe_int(provider_ids.get("Tvdb"))` | OK |
| L182 (search_items, Tmdb) | `int(provider_ids["Tmdb"])` | `_safe_int(provider_ids.get("Tmdb"))` | OK |
| L184 (search_items, Tvdb) | `int(provider_ids["Tvdb"])` | `_safe_int(provider_ids.get("Tvdb"))` | OK |
| L247 (find_by_tmdb_id, Tmdb) | `int(item_tmdb_id)` | `_safe_int(item_tmdb_id)` | OK |
| L249 (find_by_tmdb_id, Tvdb) | `int(provider_ids["Tvdb"])` | `_safe_int(provider_ids.get("Tvdb"))` | OK |

- [x] 6 appels remplaces
- [x] Aucun appel `int(provider_ids[` restant dans le fichier
- [x] Utilisation de `.get()` au lieu de `[]` (evite aussi les KeyError)

### S3 - Dependances supprimees

| Dependance | Presente dans pyproject.toml | Status |
|------------|------------------------------|--------|
| fastapi | Non | OK - supprimee |
| uvicorn | Non | OK - supprimee |
| aiohttp | Non | OK - supprimee |
| httpx | Oui (`httpx>=0.26.0`) | OK - conservee |

- [x] Structure TOML valide (tomllib parse OK)
- [x] 12 dependances restantes coherentes avec le projet

### S4 - .dockerignore

- [x] Fichier `.dockerignore` existe a la racine
- [x] Exclut `.git/`
- [x] Exclut `.venv/` et `venv/`
- [x] Exclut `logs/`
- [x] Exclut `data/`
- [x] Exclut `__pycache__/`, `*.pyc`, `*.pyo`
- [x] Exclut `.env` et `.env.*`
- [x] Exclut `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`
- [x] Exclut `.idea/`, `.vscode/`
- [x] Exclut `.backlog/`
- [x] Exclut `*.md` MAIS preserve `!README.md` (requis pour pip install)
- [x] Exclut `docker-compose*.yml`

---

## Couverture des Specs

| Critere d'Acceptation | Status |
|----------------------|--------|
| S1: Fonction `_safe_int()` ajoutee dans jellyfin.py | OK |
| S1: Les 6 appels `int()` sur provider IDs remplaces | OK |
| S1: Slugs type `73375-jack-ryan` correctement parses | OK |
| S1: Valeurs non-numeriques retournent None sans crash | OK |
| S1: Le code compile sans erreur | OK |
| S3: fastapi supprime de pyproject.toml | OK |
| S3: uvicorn supprime de pyproject.toml | OK |
| S3: aiohttp supprime de pyproject.toml | OK |
| S4: Fichier .dockerignore cree a la racine | OK |
| S4: Exclut .git, .venv, logs, data, caches, IDE | OK |

---

## Bugs Trouves

Aucun bug trouve.

---

## Verdict Final

### ACCEPTE

Tous les criteres d'acceptation sont valides pour les scopes S1, S3 et S4:

- **S1**: La fonction `_safe_int()` est correctement implementee et gere tous les cas specifies (None, vide, entier pur, slug, non-numerique). Les 6 appels `int()` directs ont ete remplaces. Le passage de `provider_ids["key"]` a `provider_ids.get("key")` ajoute une protection supplementaire contre les KeyError.
- **S3**: Les 3 dependances inutiles (fastapi, uvicorn, aiohttp) ont ete supprimees. Le TOML reste valide et httpx est conserve.
- **S4**: Le `.dockerignore` est complet et preserve README.md necessaire au build pip.

Note: Les scopes S2 (fermeture issues #2/#3) et S5 (reponse issue #1) sont des actions GitHub CLI hors perimetre de ce rapport backend.
