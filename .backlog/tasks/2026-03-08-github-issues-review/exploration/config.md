# Exploration Config et Infrastructure

## Dependances Inutiles (HAUTE PRIORITE)
- **fastapi** + **uvicorn**: declares mais JAMAIS importes (~500MB image)
- **aiohttp**: declare mais JAMAIS importe, redondant avec httpx

## Docker
- Multi-stage build OK
- Manque .dockerignore (copie logs/, data/, config/ inutilement)
- docker-compose.portainer.yml: syntaxe ${VAR:?...} non supportee par Portainer
- Pas de resource limits dans docker-compose

## Documentation
- Bonne qualite globale (8.5/10)
- Manque: troubleshooting, performance tuning, guide proxy
- README manque section "Limitations connues"

## CI/CD
- Pas de tests en CI
- Pas de scan securite images
- Pas de notification si build echoue
