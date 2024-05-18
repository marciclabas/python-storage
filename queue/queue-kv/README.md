# Queue: Key-Value

> Queue implementation based on [`kv.api`](https://pypi.org/project/kv-api/)

```python
pip install queue-kv

from q.kv import QueueKV
```

## Usage

- Use an arbitrary `KV` implementation:

```python
from kv.api import KV
from q.kv import QueueKV

kv: KV[tuple[str, int]] = ...
queue = QueueKV(kv)
```

- Or some of the predefined ones:

```python
q = QueueKV.fs(dict[str, tuple[float, str]], 'path/to/data')
q = QueueKV.sqlite(MyDataclass, 'path/to/db.sqlite')
```
