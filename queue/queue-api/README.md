# Queue Api

> ABC for asynchronous, point-readable, exception-free read/write queues

```python
pip install queue-api

from q.api import Queue, ReadQueue, WriteQueue #, ...
```

## Interfaces

### `ReadQueue[A]`

```python
A = TypeVar('A', covariant=True)

class ReadQueue(Generic[A]):
  async def pop(self) -> Either[QueueError, tuple[str, A]]:
    ...

  async def pop(self, id: str) -> Either[ReadError, A]:
    ...

  async def read(self) -> Either[QueueError, tuple[str, A]]:
    ...

  async def read(self, id: str) -> Either[ReadError, A]:
    ...

  async def items(self) -> AsyncIter[Either[QueueError, tuple[str, A]]]:
    ...
  
  async def keys(self) -> AsyncIter[Either[ReadError, str]]:
    ...
  
  async def values(self) -> AsyncIter[Either[ReadError, A]]:
    ...
```

### `WriteQueue[A]`

```python
A = TypeVar('A', contravariant=True)

class WriteQueue(Generic[A]):
  async def push(self, key: str, value: A) -> Either[QueueError, None]:
    ...
```

### `Queue[A] = ReadQueue[A] & WriteQueue[A]`

### `AppendQueue[A]`

```python
class AppendQueue(WriteQueue[Sequence[A]], Generic[A]):
  async def append(self, id: str, values: Sequence[A], *, create: bool) -> bool:
    ...
```

## R/W differences

In general, a `Queue[A]` can be treated as an `AsyncIterable[A]`. However, there are some distintions between `Read-` and `WriteQueues`

### Variance

> `ReadQueue[A]` is *covariant*

Since `ReadQueue` is immutable, someone expecting a `ReadQueue[Animal]` will be happy with a `ReadQueue[Cat]`.

> `WriteQueue[A]` is *contravariant*

This is a bit of a weird one: `WriteQueue` is mutable but not readable. Thus, someone expecting a `WriteQueue[Cat]` will be happy with a `WriteQueue[Animal]`.
  
### Operations

> `ReadQueue`s can be `map`-ed and `filter`-ed. This is akin to `map` and `filter` on `AsyncIter`-ables.

> `WriteQueue`s can be `premap`-ed and `prefilter`-ed.

Again a bit of a weird one: let's use an example:

```python
async def cats(queue: WriteQueue[tuple[str, Cat]]):
  await queue.push('key1', ('Garfield', Cat(...)))
  await queue.push('key2', ('Puss in Boots', Cat(...)))

q_cats: Queue[Cat] = ...
```

Here, our `q_cats` queue wants `Cat`s, but `cats` insists on yielding a tuple `(name, Cat)`. So, we can `premap` a function to adapt the queue:

```python
await cats(q_cats.premap(lambda t: t[1]))
```

## Composition

`Queue[B]` is both a `ReadQueue[B]` and a `WriteQueue[B]`. However, we'll generally want to have a producer function (that receives a `WriteQueue[A]`) and a consumer function, that receives a `ReadQueue[C]`.

Still, for whatever reason, we may want to actually store data in a `Queue[B]`. The setup is then as follows:

```python
queue: Queue[B] = ...

async def producer(queue: WriteQueue[A]):
  ...

async def consumer(queue: ReadQueue[C]):
  ...

producer(queue.premap(f)) # f :: A -> B
consumer(queue.map(g)) # g :: B -> C
```

Now, `premap` always returns a `WriteQueue`; `map` always a `ReadQueue`. Thus, we can compose indefinetely in either direction:

```python
producer(queue.premap(f1).premap(f2).premap(f3))
consumer(queue.map(g1).map(g2).map(g3))
```

## Implementations

- [`queue-kv`](https://pypi.org/project/queue-kv/): based on [`kv.api`](https://pypi.org/project/kv-api/)
