"""Typer CLI entry points."""

from __future__ import annotations

import json
import logging

import typer

from app.config import load_settings
from app.db.database import initialize_database
from app.logging_config import configure_logging
from app.services.tracker_importer import import_tracker

app = typer.Typer(help="dp-vee-core command line interface")
logger = logging.getLogger(__name__)


@app.command()
def run() -> None:
    """Initialize configuration, logging, and database."""

    settings = load_settings()
    configure_logging(settings.log_level)
    initialize_database(settings.db_path)
    typer.echo("VEE Core initialized")


@app.command("import-tracker")
def import_tracker_command(file: str = typer.Option(..., "--file", help="Path to tracker XLSX")) -> None:
    """Import Universal Tracker records into licenses table."""

    settings = load_settings()
    configure_logging(settings.log_level)

    summary = import_tracker(file)
    logger.info("Tracker import completed: %s", summary)
    typer.echo(json.dumps(summary, indent=2))
