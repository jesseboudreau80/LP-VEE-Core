# dp-vee-core

Production-grade scaffolding for a modular Licensing & Permitting Virtual Employee (VEE) system.

> This repository is intentionally architecture-only for v1. No document extraction logic, Playwright implementation, or business rules are implemented yet.

## Tech Stack
- Python 3.11
- SQLite (v1)
- Typer (CLI)
- Pydantic
- python-dotenv
- Docker / Docker Compose

## Setup Instructions
1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your environment file:
   ```bash
   cp .env.example .env
   ```
4. Update `.env` values if needed.

## How to Run Locally
```bash
python -m app.main run
```

Expected output:
```text
VEE Core initialized
```

## How to Run in Docker
Build and run with Docker Compose:
```bash
docker compose up --build
```

The service executes:
```bash
python -m app.main run
```

## Tracker Importer
Import a tracker XLSX into the SQLite database:
```bash
python -m app.main import-tracker data/tracker/tracker.xlsx
```

If no path is provided, the CLI uses `TRACKER_PATH/tracker.xlsx`. The command prints a deterministic summary like:
```json
{
  "processed": 2,
  "inserted": 2,
  "skipped": 0,
  "updated": 0
}
```

## Renewal Evaluation
Recalculate license statuses based on expiration timelines and renewal windows:
```bash
python -m app.main evaluate-licenses
```
Outputs a JSON summary of counts across status categories.

## Folder Explanation
```text
dp-vee-core/
├── docker-compose.yml        # Container orchestration for local runtime
├── Dockerfile                # Python 3.11 container image definition
├── .env.example              # Required environment variable template
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── app/
│   ├── main.py               # Module entrypoint (python -m app.main)
│   ├── config.py             # Environment loading and validation
│   ├── cli.py                # Typer CLI commands
│   ├── logging_config.py     # Central logging setup
│   ├── db/
│   │   ├── models.py         # SQLite DDL for v1 tables
│   │   ├── database.py       # Database connection and initialization
│   │   ├── migrations.py     # Migration placeholder
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Core service layer scaffolds
│   ├── interfaces/           # External integration interface scaffolds
│   ├── utils/                # Utility placeholders
├── data/                     # Runtime data directories
│   ├── inbox/
│   ├── outbox/
│   ├── tracker/
├── logs/                     # Log output directory
└── tests/                    # Test suite scaffolding
```

## Configuration
Required environment variables:
- `DB_PATH`
- `CONFIDENCE_THRESHOLD`
- `INBOX_PATH`
- `OUTBOX_PATH`
- `TRACKER_PATH`
- `LOG_LEVEL`

## Future Roadmap
- Add structured migrations and schema versioning.
- Implement document intake parsing pipeline.
- Add orchestration workflows and business rules.
- Implement integrations (Agilence, M365, browser auth).
- Expand automated tests and CI/CD checks.
