"""Typer CLI entry points."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from app.config import load_settings
from app.db.database import initialize_database
from app.logging_config import configure_logging
from app.services.vee_orchestrator import evaluate_licenses
from app.services.tracker_importer import TrackerImporter

app = typer.Typer(help="dp-vee-core command line interface")


@app.command()
def run() -> None:
    """Initialize configuration, logging, and database."""

    settings = load_settings()
    configure_logging(settings.log_level)
    initialize_database(settings.db_path)
    typer.echo("VEE Core initialized")


@app.command("import-tracker")
def import_tracker(tracker_file: str | None = typer.Argument(None, help="Path to tracker XLSX file")) -> None:
    """Import tracker XLSX rows into the database."""

    settings = load_settings()
    configure_logging(settings.log_level)
    initialize_database(settings.db_path)

    default_path = Path(settings.tracker_path) / "tracker.xlsx"
    path = Path(tracker_file) if tracker_file else default_path

    importer = TrackerImporter(settings.db_path)
    summary = importer.import_tracker(str(path))
    typer.echo(json.dumps(summary, sort_keys=True, indent=2))


@app.command("evaluate-licenses")
def evaluate_licenses_cmd() -> None:
    """Evaluate tracker entries and update license statuses."""

    settings = load_settings()
    configure_logging(settings.log_level)
    initialize_database(settings.db_path)

    summary = evaluate_licenses(settings.db_path)
    typer.echo(json.dumps(summary, sort_keys=True, indent=2))
