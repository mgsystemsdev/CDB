#!/bin/bash

DB=${1:-":memory:"}
ITEM=${2:-"demo"}
PYTHONPATH="$(pwd)/src" python3 -m src.main_cli --db "$DB" --item-id "$ITEM" --date $(date -v-2d +%Y-%m-%d) --hours 1.5
PYTHONPATH="$(pwd)/src" python3 -m src.main_cli --db "$DB" --item-id "$ITEM" --date $(date -v-1d +%Y-%m-%d) --hours 1.5
PYTHONPATH="$(pwd)/src" python3 -m src.main_cli --db "$DB" --item-id "$ITEM" --date $(date +%Y-%m-%d) --hours 1.5
