# Key-Value: SQLite3

> Implementation of the `KV[T]`async Key-Value ABC, over python's `sqlite3`

```bash
pip install kv-sqlite-sync
```

## Usage

### Custom serialization

```python
from kv.sqlite import SQLiteKV, InvalidData
from haskellian import Either, Left, Right
import json

def safe_parse(x: str) -> Either[InvalidData, dict]:
  try:
    return Right(json.loads(x))
  except Exception as e:
    return Left(InvalidData(e))
  
kv = SQLiteKV[dict].at(
  db_path='mydb.sqlite', table='my-jsons',
  dtype='JSON', parse=json.loads, dump=json.dumps
)

await kv.insert('key1', {'a': 1, 'b': 2})
```

### Pydantic-validated types

```python
from kv.sqlite import SQLiteKV

kv = SQLiteKV.validated(
  tuple[str, int],
  db_path='mydb.sqlite', table='my-tuples',
)

await kv.insert('key1', ('a', 1))
```