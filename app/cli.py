"""Typer CLI entry points."""

from __future__ import annotations

import typer

from app.config import load_settings
from app.db.database import initialize_database
from app.logging_config import configure_logging

app = typer.Typer(help="dp-vee-core command line interface")


@app.command()
def run() -> None:
    """Initialize configuration, logging, and database."""

    settings = load_settings()
    configure_logging(settings.log_level)
    initialize_database(settings.db_path)
    typer.echo("VEE Core initialized")
