# Key-Value API

> ABC for a an async key-value store

```bash
pip install kv-api
```

## Spec

```python
class KV(Generic[T]):
  
  async def insert(self, key: str, value: T) -> Either[DBError, None]:
    ...

  async def read(self, key: str) -> Either[ReadError, T]:
    ...

  async def delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    ...

  async def items(self, batch_size: int | None = None) -> AsyncIter[Either[DBError | InvalidData, tuple[str, T]]]:
    ...

  async def has(self, key: str) -> Either[DBError, bool]:
    ...
  
  async def keys(self) -> Either[DBError, Sequence[str]]:
    ...

  async def values(self, batch_size: int | None = None) -> AsyncIter[Either[DBError|InvalidData, T]]:
    ...

  async def copy(self, key: str, to: KV[T], to_key: str) -> Either[DBError|InexistentItem, None]:
    ...

  async def move(self, key: str, to: KV[T], to_key: str) -> Either[DBError|InexistentItem, None]:
    ...
```

## Usage

- All functions return `Either` instead of throwing
- For chaining multiple operations, it is recommended to use a kind of do notation for `Either`, using exceptions
  - `Either.unsafe()` unwraps the right value or raises `IsLeft`

```python
from kv.api import KV, DBError
from haskellian import Either, IsLeft

async def multi_copy(key_from: str, keys_to: str, data: KV[bytes]) -> Either[DBError, None]:
  try:
    value = (await data.read(key_from)).unsafe()
    for key in keys_to:
      (await data.insert(key, value)).unsafe()
    return Right(None)
  except IsLeft as e:
    return Left(e.value)
```

## Extensions

### `AppendableKV[T]`

> A `KV[Sequence[T]]` that supports appending

```python
class AppendableKV(KV[Sequence[T]], Generic[T]):
  async def append(self, id: str, values: Sequence[T], *, create: bool) -> Either[DBError|InexistentItem, None]:
    ...
```

### `LocatableKV[T]`

> A `KV[T]` whose items can be accessed via some URL

```python
class LocatableKV(KV[T], Generic[T]):
  def url(self, id: str) -> str:
    ...
```

## Implementations

- [`kv-fs`](https://pypi.org/project/kv-fs/): on the local filesystem
- [`kv-sqlite-sync`](https://pypi.org/project/kv-sqlite-sync/): on SQLite with python's `sqlite3` synchronous interface
- [`kv-rest`](https://pypi.org/project/kv-rest/): client, over HTTP, to a server-side KV
- [`kv-azure-blob`](https://pypi.org/project/kv-azure-blob/): on Azure Blob Storage