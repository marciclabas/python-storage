from typing_extensions import Generic, Never, TypeVar, Callable, Awaitable, overload, AsyncIterable, AsyncIterator, TypeGuard, Sequence
from abc import ABC, abstractmethod
from haskellian import AsyncIter, promise as P, Either, Left, Right, iter as I
from .errors import QueueError, ReadError, InexistentItem

A = TypeVar('A', covariant=True)
B = TypeVar('B', covariant=True)
E = TypeVar('E', covariant=True)

class ReadQueue(ABC, AsyncIterator[Either[QueueError, tuple[str, A]]], Generic[A]):
  
  @abstractmethod
  async def _read(self, id: str | None, remove: bool) -> Either[ReadError, tuple[str, A]]:
    ...

  @overload
  async def pop(self) -> Either[QueueError, tuple[str, A]]:
    ...
  @overload
  async def pop(self, id: str) -> Either[ReadError, A]:
    ...

  async def pop(self, id: str | None = None) -> Either[ReadError, A | tuple[str, A]]:
    match await self._read(id, remove=True):
      case Right((k, v)):
        return Right((k, v) if id is None else v)
      case err:
        return err
  
  @overload
  async def read(self) -> Either[QueueError, tuple[str, A]]:
    ...
  @overload
  async def read(self, id: str) -> Either[ReadError, A]:
    ...
  
  async def read(self, id: str | None = None) -> Either[ReadError, A | tuple[str, A]]:
    match await self._read(id, remove=False):
      case Right((k, v)):
        return Right((k, v) if id is None else v)
      case err:
        return err
      
  @abstractmethod
  def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, A]]]:
    ...

  def items(self) -> AsyncIter[Either[QueueError, tuple[str, A]]]:
    return AsyncIter(self._items())
  
  def keys(self) -> AsyncIter[Either[ReadError, str]]:
    return AsyncIter(e | I.fst async for e in self._items())
  
  def values(self) -> AsyncIter[Either[ReadError, A]]:
    return AsyncIter(e | I.snd async for e in self._items())
  
  async def __anext__(self) -> Either[QueueError, tuple[str, A]]:
    return await self.pop()
  
  def iter(self):
    async def iterate():
      while (x := await self.pop()):
        yield x
    return AsyncIter(iterate())
  
  __aiter__ = iter
  
  def map(self, f: Callable[[A], B]) -> 'ReadQueue[B]':
    """Maps `f` over self. Returns a new queue, but `self` is still mutated when popping from the new queue"""
    return qmap(self, lambda kv: P.of((kv[0], f(kv[1]))))
  
  def map_kv(self, f: Callable[[str, A], B]) -> 'ReadQueue[B]':
    """Map but `f` receives both key and value"""
    return qmap(self, lambda kv: P.of((kv[0], f(*kv))))
  
  def map_k(self, f: Callable[[str], B]) -> 'ReadQueue[B]':
    """Map but `f` receives the key"""
    return qmap(self, lambda kv: P.of((kv[0], f(kv[0]))))
  
  def map_kvt(self, f: Callable[[tuple[str, A]], B]) -> 'ReadQueue[B]':
    """Map but `f` receives both key and value as a tuple"""
    return qmap(self, lambda kv: P.of((kv[0], f(kv))))
  
  def amap(self, f: Callable[[A], Awaitable[B]]) -> 'ReadQueue[B]':
    """Map but `f` is asynchronous"""
    async def mapper(kv: tuple[str, A]):
      return kv[0], await f(kv[1])
    return qmap(self, mapper)
  
  def amap_kv(self, f: Callable[[str, A], Awaitable[B]]) -> 'ReadQueue[B]':
    """Map but `f` is asynchronous and receives both key and value"""
    async def mapper(kv: tuple[str, A]):
      return kv[0], await f(*kv)
    return qmap(self, mapper)
  
  def amap_k(self, f: Callable[[str], Awaitable[B]]) -> 'ReadQueue[B]':
    """Map but `f` is asynchronous and receives the key"""
    async def mapper(kv: tuple[str, A]):
      return kv[0], await f(kv[0])
    return qmap(self, mapper)
  
  def amap_kvt(self, f: Callable[[tuple[str, A]], Awaitable[B]]) -> 'ReadQueue[B]':
    """Map but `f` is asynchronous and receives both key and value as a tuple"""
    async def mapper(kv: tuple[str, A]):
      return kv[0], await f(kv)
    return qmap(self, mapper)

  @overload
  def filter(self, pred: Callable[[A], TypeGuard[B]]) -> 'ReadQueue[B]': ...
  @overload
  def filter(self, pred: Callable[[A], bool]) -> 'ReadQueue[A]': ...
  def filter(self, pred): # type: ignore
    return qfilter(self, lambda _, v: pred(v))
  
  @overload
  def filter_kv(self, pred: Callable[[str, A], TypeGuard[B]]) -> 'ReadQueue[B]': ...
  @overload
  def filter_kv(self, pred: Callable[[str, A], bool]) -> 'ReadQueue[A]': ...
  def filter_kv(self, pred): # type: ignore
    return qfilter(self, pred)
  
  def partition(self, pred: Callable[[A], bool]) -> 'tuple[ReadQueue[A], ReadQueue[A]]':
    """Returns `self.filter(pred), self.filter(!pred)`"""
    return self.filter(pred), self.filter(lambda x: not pred(x))
  
  def partition_kv(self, pred: Callable[[str, A], bool]) -> 'tuple[ReadQueue[A], ReadQueue[A]]':
    """Returns `self.filter_kv(pred), self.filter_kv(!pred)`"""
    return self.filter_kv(pred), self.filter_kv(lambda *x: not pred(*x))
  
  
class qmap(ReadQueue[B], Generic[A, B]):
  
  def __init__(self, q: ReadQueue[A], f: Callable[[tuple[str, A]], Awaitable[tuple[str, B]]]):
    self._wrapped = q
    self._mapper = f
    __name__ = f'Mapped{repr(self)}'

  async def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, B]]]:
    async for e in self._wrapped._items():
      if e.tag == 'left':
        yield e # type: ignore
      else:
        yield Right(await self._mapper(e.value))

  async def _read(self, id: str | None, remove: bool) -> Either[ReadError, tuple[str, B]]:
    match await self._wrapped._read(id, remove):
      case Right((k, v)):
        return Right(await self._mapper((k, v)))
      case err:
        return err # type: ignore
      
class qfilter(ReadQueue[A], Generic[A]):

  def __init__(self, queue: ReadQueue[A], pred: Callable[[str, A], bool]):
    self._pred = pred
    self._queue = queue

  async def _point_read(self, id: str, remove: bool) -> Either[ReadError, tuple[str, A]]:
    e = await self._queue.read(id)
    if e.tag == 'left':
      return e # type: ignore
    item = e.value
    if not self._pred(id, item):
      return Left(InexistentItem(id, detail=f'"{id}" exists but has been filtered out by {self._pred}'))
    if remove:
      await self._queue.pop(id)
    return Right((id, item))

  async def _read_any(self, remove: bool) -> Either[QueueError, tuple[str, A]]:
    async for e in self._items():
      if e.tag == 'left':
        return e
      id, item = e.value
      if remove:
        await self._queue.pop(id)
      return Right((id, item))
    return Never

  async def _read(self, id: str | None, remove: bool) -> Either[ReadError, tuple[str, A]]:
    return await (self._read_any(remove) if id is None else self._point_read(id, remove))
  
  async def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, A]]]:
    async for e in self._queue._items():
      if e.tag == 'left':
        yield e
      elif self._pred(*e.value):
        yield e
