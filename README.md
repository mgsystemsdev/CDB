# Practice Tracker

A desktop-first practice tracking software that:

- Logs coding sessions with tags, notes, and difficulty.
- Stores data primarily in **pandas DataFrames** and **numpy arrays**, with SQLite for persistence/sync.
- Ingests Git commit history and attributes it to sessions.
- Tracks hours, points, streaks, and progress over time.
- Publishes snapshots to Supabase for a recruiter-friendly public portfolio.
- Renders read-only dashboards in Streamlit.

## Tech Stack
- **Python 3.11+**
- **PySide6** for desktop UI
- **Pandas + Numpy** for data tables and analytics
- **SQLite + SQLAlchemy + Alembic** for storage
- **Supabase** for cloud sync
- **Streamlit** for recruiter-facing dashboards

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Run CLI

### In-Memory
Run the CLI with in-memory database:
```bash
PYTHONPATH="$(pwd)/src" python3 -m src.main_cli --hours 2
```

### Persistent
Run the CLI with SQLite database:
```bash
PYTHONPATH="$(pwd)/src" python3 -m src.main_cli --db smart.db --item-id demo --target-hours 5 --hours 2
```

## Run Tests
Run all tests:
```bash
make test
```

## Troubleshooting

### PYTHONPATH
Ensure `PYTHONPATH` is set to the project root:
```bash
export PYTHONPATH="$(pwd)/src"
```

# CDB
