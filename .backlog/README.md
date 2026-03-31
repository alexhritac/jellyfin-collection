# Backlog - Jellyfin Collection (JFC)

Structure geree par agent-factory.

## Architecture Centree

Chaque tache et bug est un dossier complet contenant tous ses fichiers.

```
.backlog/
├── tasks/                     # Chaque tache = sous-dossier horodate
│   └── [YYYY-MM-DD]-[slug]/
│       ├── task.md            # Description + progression
│       ├── spec.md            # Specifications
│       ├── plan.md            # Plan d'implementation
│       ├── kpis.md            # Metriques Poker Planning
│       ├── exploration/       # Resultats analyse initiale
│       ├── qa/                # Rapports QA versiones
│       │   ├── backend/       # 01-timestamp.md, 02-timestamp.md...
│       │   └── frontend/
│       ├── review/            # Rapports Review versiones
│       │   ├── backend/
│       │   ├── frontend/
│       │   └── arch-*/        # Si architectes detectes
│       ├── retrospective.md
│       └── report.md          # Rapport final consolide
├── bugs/                      # Chaque bug = sous-dossier horodate
│   ├── active/
│   │   └── [YYYY-MM-DD]-[slug]/
│   │       ├── bug.md
│   │       ├── exploration/
│   │       ├── analysis.md
│   │       ├── solution/
│   │       ├── qa/
│   │       └── report.md
│   └── resolved/
├── ideas/
│   ├── pending/               # Idees en attente
│   ├── converted/             # Converties en taches
│   └── rejected/              # Rejetees avec raison
└── imports/                   # Backlogs externes (Jira, CSV...)
```

## Commandes

- `/agent-factory:task <desc>` - Nouvelle tache (cree un dossier complet)
- `/agent-factory:debug <probleme>` - Nouveau bug (cree un dossier complet)
- `/agent-factory:idea <desc>` - Capturer une idee
- `/agent-factory:audit` - Audit technique du projet
