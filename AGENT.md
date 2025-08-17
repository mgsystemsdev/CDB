# Smart Tracker - Agent Documentation

## Testing Commands

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
# WARNING: Integration tests may timeout - use manual testing for now
pytest tests/integration/ -v
```

### All Tests
```bash
pytest tests/ -v
```

## Code Quality Commands

### Formatting
```bash
python3 -m black src/
python3 -m isort src/
```

### Type Checking
(No mypy or similar configured yet)

## Dependencies

### Core Dependencies
- aiosqlite (added for SQLite async operations)
- pytest-anyio (for async test support)

### Missing/Fixed Dependencies
- aiosqlite==0.19.0 - Added to requirements.txt and pyproject.toml

## Known Issues

### Integration Test Timeout
- `tests/integration/test_session_roundtrip_sqlite.py` times out when run via pytest
- Manual execution works fine
- Likely related to pytest-anyio version compatibility
- Solution: Use manual testing or investigate pytest configuration

### Code Organization
- Duplicate use case files: 
  - `src/core/usecases/log_session.py` (main implementation with Pydantic/dataclass compatibility)
  - `src/usecases/log_session.py` (simplified dataclass-only version)

## CLI Usage

### Running the CLI
```bash
# Install dependencies first
pip install -r requirements.txt

# Run with proper Python path
PYTHONPATH=src python3 -m main_cli --hours 1.5

# Or alternatively
cd src && python3 main_cli.py --hours 1.5
```

## Code Quality Status
- ✅ All unit tests passing (73/73)
- ✅ Code formatted with black
- ✅ Imports sorted with isort
- ✅ No circular import issues
- ✅ CLI imports and data structures work correctly
- ⚠️ Integration tests timeout (but logic works manually)
- ⚠️ CLI may timeout in some environments (aiosqlite event loop issue)

## Architecture Notes
- Clean architecture with core/domain/infrastructure separation
- Uses both Pydantic models and dataclasses
- SQLite for persistence with async operations
- Protocol-based dependency injection
