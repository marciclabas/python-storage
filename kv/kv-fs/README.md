# Key-Value: Filesystem

> Implementation of the `KV[T]`async Key-Value ABC, on the filesystem

```bash
pip install kv-fs
```

## Usage

### Already serialized data (`str` or `bytes`)

```python
from kv.fs import FilesystemKV

data = FilesystemKV[bytes]('path/to/data')
# and then use it as you'd a KV[bytes]
```

### Custom serialization

```python
from kv.fs import FilesystemKV, InvalidData
from haskellian import Either, Left, Right
import json

def safe_parse(x: bytes) -> Either[InvalidData, dict]:
  try:
    return Right(json.loads(x))
  except Exception as e:
    return Left(InvalidData(e))

data = FilesystemKV[dict](
  base_path='path',
  extension='.json',
  dump=json.dumps,
  parse=safe_parse
)
# and then use it as you'd a KV[dict]
```

### Pydantic-validated types

```python
from kv.fs import FilesystemKV, InvalidData

kv = FilesystemKV.validated(tuple[str, int], 'path/to/data') # any JSON/pydantic serializable type should work
# and then use it as you'd a KV[tuple[str, int]]

await kv.read('key-with-invalid-data') # Left(InvalidData(ValidationError(...))
```

## `AppendableKV[T]`

```python
from kv.fs import FilesystemAppendKV

kv = FilesystemKV.validated(tuple[str, int], 'path/to/data') # stores data as ndjson
await kv.append('key', [('first', 1), ('second', 2)])
```