# Exploration Tests et Qualite

## Couverture: 23% (2,580 lignes test / 11,207 lignes source)

### Modules Bien Testes
- models/ (87-115%) - Excellent
- parsers/kometa.py (105%) - Excellent
- services/media_matcher.py (167%) - Excellent
- core/config.py (60%) - Bon

### Modules Sans Tests (CRITIQUE)
- services/collection_builder.py (1,348 lignes, 0 tests) - TRES CRITIQUE
- cli.py (1,000+ lignes, 0 tests) - HAUTE
- clients/jellyfin.py (566 lignes, 0 tests) - CRITIQUE
- clients/discord.py (613 lignes, 0 tests) - HAUTE
- services/runner.py (544 lignes, 0 tests) - CRITIQUE
- clients/radarr.py, sonarr.py, trakt.py, signal.py, telegram.py - HAUTE

### CI/CD
- Seul workflow: docker-build.yml (build + push images)
- AUCUN test, linting, coverage, type checking en CI

### Code Smells
- 8 bare Exception catches
- 0 TODOs/FIXMEs dans le code
- 0 type: ignore ou noqa
