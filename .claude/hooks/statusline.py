#!/usr/bin/env python3
"""
Status Line pour Agent Factory - Affiche la progression des workflows.

Ce script est appele par Claude Code pour afficher une ligne de statut
personnalisee montrant la progression des workflows agent-factory.

Usage dans .claude/settings.json:
{
  "statusLine": {
    "type": "command",
    "command": "python \".claude/hooks/statusline.py\""
  }
}

Format affiche:
  [Opus] 42% | Task: auth-login | Phase 4/7 Implementation | Vague 2/3 | 5/8 taches
"""

import json
import os
import sys
from pathlib import Path

# Couleurs ANSI
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


def find_project_root():
    """Trouve la racine du projet."""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])

    current = Path.cwd()
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    return Path.cwd()


def load_workflow_progress(project_root: Path) -> dict | None:
    """Charge la progression du workflow."""
    progress_file = project_root / ".claude" / "workflow-progress.json"

    if not progress_file.exists():
        return None

    try:
        with open(progress_file, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def format_phase_name(phase: str) -> str:
    """Formate le nom de la phase pour l'affichage."""
    phase_names = {
        "exploration": "Exploration",
        "specs": "Specs",
        "planning": "Planning",
        "implementation": "Implementation",
        "qa": "QA",
        "review": "Review",
        "retrospective": "Retro",
        # Debug phases
        "analysis": "Analyse",
        "solution": "Solution",
        "validation": "Validation",
        "report": "Rapport",
        "archivage": "Archivage"
    }
    return phase_names.get(phase.lower(), phase.capitalize())


def format_progress_bar(current: int, total: int, width: int = 10) -> str:
    """Cree une barre de progression (ASCII-safe for Windows)."""
    if total == 0:
        return "-" * width

    filled = int((current / total) * width)
    empty = width - filled

    return "#" * filled + "-" * empty


def format_workflow_status(progress: dict) -> str:
    """Formate le statut du workflow pour la status line."""
    parts = []

    workflow_type = progress.get("type", "task")
    name = progress.get("name", "")

    # Type et nom (ASCII-safe for Windows)
    if workflow_type in ("task", "feature"):
        type_icon = "[TASK]"
    elif workflow_type == "debug":
        type_icon = "[DEBUG]"
    else:
        type_icon = "[WORK]"

    # Nom court (max 20 chars)
    short_name = name[:20] + "..." if len(name) > 20 else name
    parts.append(f"{type_icon} {Colors.BRIGHT_CYAN}{short_name}{Colors.RESET}")

    # Phase
    current_phase = progress.get("current_phase", 0)
    total_phases = progress.get("total_phases", 7)
    phase_name = progress.get("phase_name", "")

    if phase_name:
        phase_display = format_phase_name(phase_name)
        parts.append(f"{Colors.YELLOW}Phase {current_phase}/{total_phases}{Colors.RESET} {phase_display}")

    # Vague (si implementation)
    current_wave = progress.get("current_wave")
    total_waves = progress.get("total_waves")

    if current_wave is not None and total_waves is not None:
        parts.append(f"{Colors.MAGENTA}Vague {current_wave}/{total_waves}{Colors.RESET}")

    # Taches
    completed_tasks = progress.get("completed_tasks", 0)
    total_tasks = progress.get("total_tasks", 0)

    if total_tasks > 0:
        progress_bar = format_progress_bar(completed_tasks, total_tasks, 8)
        parts.append(f"{Colors.GREEN}{progress_bar}{Colors.RESET} {completed_tasks}/{total_tasks}")

    # QA/Review iterations
    qa_iteration = progress.get("qa_iteration")
    review_iteration = progress.get("review_iteration")

    if qa_iteration is not None and qa_iteration > 0:
        parts.append(f"{Colors.BLUE}QA#{qa_iteration}{Colors.RESET}")

    if review_iteration is not None and review_iteration > 0:
        parts.append(f"{Colors.BLUE}Rev#{review_iteration}{Colors.RESET}")

    return " | ".join(parts)


def main():
    """Point d'entree principal."""
    # Lire les donnees de Claude Code depuis stdin
    claude_data = {}
    try:
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
            if input_data.strip():
                claude_data = json.loads(input_data)
    except (json.JSONDecodeError, IOError):
        pass

    # Extraire les infos de base de Claude
    model_name = claude_data.get("model", {}).get("display_name", "Claude")
    # Raccourcir le nom du modele
    if "Opus" in model_name:
        model_short = "Opus"
    elif "Sonnet" in model_name:
        model_short = "Sonnet"
    elif "Haiku" in model_name:
        model_short = "Haiku"
    else:
        model_short = model_name[:10]

    context_used = claude_data.get("context_window", {}).get("used_percentage", 0)

    # Construire la partie de base
    base_parts = []
    base_parts.append(f"{Colors.DIM}[{model_short}]{Colors.RESET}")

    # Indicateur de contexte avec couleur selon le niveau
    if context_used > 80:
        ctx_color = Colors.RED
    elif context_used > 60:
        ctx_color = Colors.YELLOW
    else:
        ctx_color = Colors.GREEN
    base_parts.append(f"{ctx_color}{context_used:.0f}%{Colors.RESET}")

    base_status = " ".join(base_parts)

    # Charger la progression du workflow
    project_root = find_project_root()
    progress = load_workflow_progress(project_root)

    if progress:
        workflow_status = format_workflow_status(progress)
        print(f"{base_status} | {workflow_status}")
    else:
        # Pas de workflow en cours - afficher juste le statut de base
        print(base_status)


if __name__ == "__main__":
    main()
