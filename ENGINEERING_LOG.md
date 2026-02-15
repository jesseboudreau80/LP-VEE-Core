
# LP-VEE-Core Engineering Log



Last Updated: 2026-02-14  

Owner: Jesse Boudreau  



---



## 🚀 Project State Summary



Phase: Phase 1A Complete  

Database: SQLite  

Interface: Typer CLI  

Runtime: Python 3.12 venv  

Test Runner: pytest  

Environment: Contabo Ubuntu 24.04 VM  



---



## ✅ Phase 1A – Tracker Importer



Implemented:



- `tracker_entries` table

- Unique constraint:

  (center_id, license_permit_type, issuing_authority)

- XLSX ingest using pandas

- Column normalization (snake_case)

- Required field validation

- Safe date parsing (ISO format)

- Upsert behavior

- Deterministic JSON summary

- Raw normalized JSON storage

- CLI command: `import-tracker`

- Test coverage (5 passing tests)



---



## 🛠 How To Run Locally



### Activate venv

```bash

cd ~/infra/LP-VEE-Core

source venv/bin/activate

Run CLI

python -m app.main run

Import Tracker

python -m app.main import-tracker data/tracker/tracker.xlsx

Run Tests

pytest

Run Tests (from anywhere)

pytest ~/infra/LP-VEE-Core

🧪 Test Status

✔ 5 tests passing

⚠ datetime.utcnow() deprecation warning



Future improvement:

Replace:



datetime.utcnow().isoformat()

With:



from datetime import datetime, UTC

datetime.now(UTC).isoformat()

🧱 Git Workflow Standard

Check status

git status

Pull latest safely

git pull --rebase origin main

Create feature branch

git checkout -b feature/<name>

Push branch

git push origin feature/<name>

🔐 SSH Status

SSH configured with:

~/.ssh/id_ed25519



Verify:



ssh -T git@github.com

📦 Python Environment Rules

DO NOT install system-wide packages.



Always:



python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

🧭 Upcoming Phases

Phase 1B

Status engine



Expiration logic



Renewal window calculations



Escalation triggers



Phase 2

Document intake parsing



Confidence scoring



Escalation service activation



Phase 3

External integrations



Agilence API



M365 notifier



Playwright auth



🧠 Engineering Principles

Always update this log after major changes



Always commit before switching branches



Never push broken tests



Keep schema changes isolated



Keep CLI commands deterministic



Think in phases, not chaos



🔥 Warp / Codex Usage Notes

Codex Model:

gpt-5.1-codex-max



If Codex acts weird:



/model

If session unclear:



/status

If permissions stuck:



/approvals

📝 Personal Note

This project is moving from scaffold → production architecture.



Maintain discipline.

This becomes foundation for:



PAWSitiveOps



Compliance automation



AI orchestration



Licensing intelligence layer



📜 Change Log (Chronological Entries)

2026-02-14

Refactored importer expiration handling.



2026-02-14

Conducted tests on the append safety system to evaluate performance and reliability. Append behavior confirmed safe. Architecture header now protected from overwrite.



