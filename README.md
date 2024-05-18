# Python Storage

> Generic, exception-free interfaces for async storage

- [`fs-tools`](fs-tools): simple, exception-free filesystem utils over python's stdlib (`os`, `shutil`, etc.)


### `KV`: interface for an async, exception-free key-value storage
- [`kv-api`](kv/kv-api/): ABC
- [`kv-sqlite-sync`](kv/kv-sqlite-sync/): SQLite3 implementation
- [`kv-fs`](kv/kv-fs/): filesystem implementation
- [`kv-rest`](kv/kv-rest/): HTTP client and server implementation

### `Queue`: interfaces for async read/write queues
- [`queue-api`](queue/queue-api/): ABC
- [`queue-kv`](queue/queue-kv/): KV-based implementation