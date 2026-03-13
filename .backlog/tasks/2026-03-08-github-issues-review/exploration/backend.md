# Exploration Backend

## Bugs Critiques Confirmes

| Severite | Localisation | Probleme |
|----------|---|---|
| CRITICAL | MediaMatcher._cache | Non thread-safe en async (race conditions) |
| HIGH | RadarrClient.load_blocklist() | Erreurs silencieuses (bare except) |
| HIGH | Kometa parser | Pas de validation chemins, template absent = silent fail |
| MEDIUM | TMDbClient genres | Types melanges (int/str) dans genres |

## Problemes Transversaux
- Pas de retry logic pour erreurs reseau
- 8 bare except clauses (radarr, sonarr, signal, config, trakt_auth)
- Cache MediaMatcher sans TTL ni invalidation
- Chemins relatifs fragiles (Windows backslash)

## Points Forts
- Architecture async solide avec httpx
- Pagination TMDb/Trakt/Jellyfin implementee
- Caching intelligent Radarr/Sonarr
