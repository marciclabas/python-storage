# Key-Value: Azure Blob

> Implementation of the `KV[T]` async Key-Value ABC, over Azure Blob Storage

([`kv-api`]((https://pypi.org/project/kv-api/)))

```bash
pip install kv-azure-blob
```

## Usage

### Raw

```python
from azure.storage.blob.aio import BlobServiceClient
from kv.azure.blob import BlobKV

bsc: BlobServiceClient = ...
kv = BlobKV[bytes](bsc)
await kv.insert('img1', b'...')
await kv.read('img2')
await kv.keys()
# etc.
```

### Pydantic-validated

```python
from dataclasses import dataclass

@dataclass
class User:
  username: str
  email: str

cc: ContainerClient = ...
kv = BlobKV.validated(User, cc)
await kv.insert('user1', User(username='user1', email='...'))
# etc.
```

## Containers

By default, keys are split across containers:

- `'users/path/to/user.txt'` goes to container `users`
- `'admins/path/to/admin.txt'` goes to container `admins`

You can customize this behavior by passing a `def split_key(key: str) -> tuple[str, str]` function.
- E.g. using `split_key=lambda key: ('container', key)` will always store in `'container'`