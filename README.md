# dp-vee-core

Production-grade scaffolding for a modular Licensing & Permitting Virtual Employee (VEE) system.

## Tech Stack
- Python 3.11
- SQLite (v1)
- Typer (CLI)
- Pydantic
- python-dotenv
- pandas
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

## Usage
### Initialize Core
```bash
python -m app.main run
```

Expected output:
```text
VEE Core initialized
```

### Tracker Import
```bash
python -m app.main import-tracker --file ./data/tracker/universal.xlsx
```

Required tracker columns (flexible name mapping supported):
- center_id
- license_permit_type
- issuing_authority
- jurisdiction
- expiration_date

Behavior:
- Normalizes spreadsheet column names to snake_case.
- Supports common column variations (e.g., `Center ID`, `center`, `License Type`).
- Skips invalid rows with warning logs when required fields are missing or dates are invalid.
- Upserts into `licenses` using unique key:
  - `(center_id, license_permit_type, issuing_authority)`
- Stores the original row payload as JSON in `raw`.
- Prints summary output:
  - `{"imported": X, "updated": Y, "skipped": Z}`

## How to Run in Docker
Build and run with Docker Compose:
```bash
docker compose up --build
```

The service executes:
```bash
python -m app.main run
```

## Folder Explanation
```text
dp-vee-core/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── README.md
├── app/
│   ├── main.py
│   ├── config.py
│   ├── cli.py
│   ├── logging_config.py
│   ├── db/
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── migrations.py
│   ├── schemas/
│   ├── services/
│   ├── interfaces/
│   ├── utils/
├── data/
│   ├── inbox/
│   ├── outbox/
│   ├── tracker/
├── logs/
└── tests/
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
- Add document extraction and validation workflows.
- Implement orchestration and escalation business rules.
- Implement production integrations (Agilence, M365, browser auth).
- Expand automated tests and CI/CD checks.
