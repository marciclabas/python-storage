from typing_extensions import Generic, TypeVar, overload, Literal, Sequence
from abc import abstractmethod
from haskellian import Either
from . import WriteQueue, Queue, QueueError, ReadError

A = TypeVar('A')

class AppendQueue(WriteQueue[Sequence[A]], Generic[A]):
  @overload
  @abstractmethod
  async def append(self, id: str, values: Sequence[A], *, create: Literal[False]) -> Either[ReadError, None]:
    """Appends `values` if it already existed. Otherwise doesn't append, and returns `Left[InexistentItem]`"""
  @overload
  @abstractmethod
  async def append(self, id: str, values: Sequence[A], *, create: Literal[True] = True) -> Either[QueueError, None]:
    """Appends `values` to `id`, creating the item if needed"""
    
class AppendableQueue(AppendQueue[A], Queue[Sequence[A]], Generic[A]):
  ...