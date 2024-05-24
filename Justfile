mod kv-api "kv/kv-api/Justfile"
mod kv-fs "kv/kv-fs/Justfile"
mod kv-rest "kv/kv-rest/Justfile"
mod kv-sql "kv/kv-sql/Justfile"
mod kv-sqlite-sync "kv/kv-sqlite-sync/Justfile"
mod kv-azure-blob "kv/kv-azure-blob/Justfile"
mod queue-api "queue/queue-api/Justfile"
mod queue-kv "queue/queue-kv/Justfile"
mod fs-tools
mod sqltypes

VENV := ".venv"
PYTHON := ".venv/bin/python"

init:
  rm -drf {{VENV}} || :
  python3.11 -m venv {{VENV}}
  {{PYTHON}} -m pip install --upgrade pip
  {{PYTHON}} -m pip install -r requirements.txt