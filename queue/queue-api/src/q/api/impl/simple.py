from typing_extensions import Generic, TypeVar, AsyncIterable, Never
from collections import OrderedDict
from .. import ReadQueue, WriteQueue, InexistentItem
from haskellian import ManagedPromise, Either, Left, Right

A = TypeVar('A')
B = TypeVar('B')

class SimpleQueue(WriteQueue[A], ReadQueue[A], Generic[A]):
  """Dead simple in-memory implementation backed by an `OrderedDict`"""

  def __init__(self):
    self.xs: OrderedDict[str, A] = OrderedDict()
    self._next = ManagedPromise()

  def __len__(self):
    return len(self.xs) # type: ignore

  async def _read(self, id: str | None = None, remove: bool = False) -> Either[InexistentItem, tuple[str, A]]:
    if id is None:
      if len(self.xs) == 0:
        await self._next
        self._next = ManagedPromise()
        return await self._read(id, remove)
      elif remove:
        return Right(self.xs.popitem())
      else:
        return Right(next(iter(self.xs.items())))
    elif id in self.xs:
      v = self.xs.pop(id) if remove else self.xs[id]
      return Right((id, v))
    else:
      return Left(InexistentItem(id))
    
  async def push(self, key: str, value: A) -> Right[Never, None]:
    self.xs[key] = value
    if not self._next.resolved:
      self._next.resolve()
    return Right(None)
  
  async def _items(self) -> AsyncIterable[Right[Never, tuple[str, A]]]:
    for x in self.xs.items():
      yield Right(x)
  