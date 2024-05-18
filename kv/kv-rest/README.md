# Key-Value: REST

> Implementation of the `KV[T]` async Key-Value ABC, over HTTP

([`kv-api`]((https://pypi.org/project/kv-api/)))

```bash
pip install kv-rest
```

## Client

```python
from kv.rest import ClientKV

client = ClientKV('http://localhost:8000', Type=tuple[str, int])
await client.insert('hello', ('world', 42))
await client.keys()
# etc.
```

## Server
```python
import uvicorn
from kv.api import KV
from kv.rest import fastapi

kv = KV[tuple[str, int]] = ...
api = fastapi(kv)

uvicorn.run(api)
```

### Server CLI

```bash
kv-rest path/to/kv.sqlite --host 0.0.0.0 --port 8000 --protocol sqlite
kv-rest path/to/kv --host 0.0.0.0 --port 8000 --protocol fs
```