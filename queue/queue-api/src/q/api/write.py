from typing_extensions import Generic, TypeVar, Callable, Awaitable, AsyncIterable, TypeGuard, overload
from haskellian import promise as P, Either, Right
from abc import ABC, abstractmethod
from .errors import QueueError

A = TypeVar('A', contravariant=True)
B = TypeVar('B', contravariant=True)

class WriteQueue(ABC, Generic[A]):

  async def iterate(self, items: AsyncIterable[tuple[str, A]]):
    """Push all `items`"""
    async for key, value in items:
      await self.push(key, value)

  @abstractmethod
  async def push(self, key: str, value: A) -> Either[QueueError, None]:
    ...

  def pusher(self, key: str) -> Callable[[A], Awaitable[Either[QueueError, None]]]:
    """Partially applied `push`"""
    return lambda value: self.push(key, value)
  
  @overload
  def prefilter(self, pred: Callable[[A], TypeGuard[B]]) -> 'WriteQueue[B]': ...
  @overload
  def prefilter(self, pred: Callable[[A], bool]) -> 'WriteQueue[A]': ...
  def prefilter(self, pred): # type: ignore
    return prefilter(self, lambda kv: P.of(pred(kv[1])))
  
  def premap(self, f: Callable[[B], A]) -> 'WriteQueue[B]':
    return premap(self, lambda kv: P.of((kv[0], f(kv[1]))))
  
  def premap_kv(self, f: Callable[[str, B], A]) -> 'WriteQueue[B]':
    """Map but `f` receives both key and value"""
    return premap(self, lambda kv: P.of((kv[0], f(*kv))))
  
  def premap_k(self, f: Callable[[str], A]) -> 'WriteQueue':
    """Map but `f` receives the key"""
    return premap(self, lambda kv: P.of((kv[0], f(kv[0]))))
  
  def premap_kvt(self, f: Callable[[tuple[str, B]], A]) -> 'WriteQueue[B]':
    """Map but `f` receives both key and value as a tuple"""
    return premap(self, lambda kv: P.of((kv[0], f(kv))))
  
  def apremap(self, f: Callable[[B], Awaitable[A]]) -> 'WriteQueue[B]':
    """Map but `f` is asynchronous"""
    async def mapper(kv: tuple[str, B]):
      return kv[0], await f(kv[1])
    return premap(self, mapper)
  
  def apremap_kv(self, f: Callable[[str, B], Awaitable[A]]) -> 'WriteQueue[B]':
    """Map but `f` is asynchronous and receives both key and value"""
    async def mapper(kv: tuple[str, B]):
      return kv[0], await f(*kv)
    return premap(self, mapper)
  
  def apremap_k(self, f: Callable[[str], Awaitable[A]]) -> 'WriteQueue':
    """Map but `f` is asynchronous and receives the key"""
    async def mapper(kv: tuple[str, B]):
      return kv[0], await f(kv[0])
    return premap(self, mapper)
  
  def apremap_kvt(self, f: Callable[[tuple[str, B]], Awaitable[A]]) -> 'WriteQueue[B]':
    """Map but `f` is asynchronous and receives both key and value as a tuple"""
    async def mapper(kv: tuple[str, B]):
      return kv[0], await f(kv)
    return premap(self, mapper)

class prefilter(WriteQueue[A], Generic[A]):
  
  def __init__(self, q: WriteQueue[A], p: Callable[[tuple[str, A]], Awaitable[bool]]):
    self._wrapped = q
    self._predicate = p
    __name__ = f'Filtered{repr(self)}'

  async def push(self, key: str, value: A) -> Either[QueueError, None]:
    if await self._predicate((key, value)):
      return await self._wrapped.push(key, value)
    return Right(None)

class premap(WriteQueue[B], Generic[A, B]):
  
  def __init__(self, q: WriteQueue[A], f: Callable[[tuple[str, B]], Awaitable[tuple[str, A]]]):
    self._wrapped = q
    self._mapper = f
    __name__ = f'Mapped{repr(self)}'

  async def push(self, key: str, value: B):
    k, v = await self._mapper((key, value))
    return await self._wrapped.push(k, v)