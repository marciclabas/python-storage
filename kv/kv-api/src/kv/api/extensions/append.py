from typing_extensions import Generic, TypeVar, overload, Literal, Sequence
from abc import ABC, abstractmethod
from haskellian import Either, Left, Right, Promise, promise as P
from ..kv import KV
from ..impl import SimpleKV
from ..errors import DBError, InexistentItem

T = TypeVar('T')

class Appendable(ABC, Generic[T]):
  @overload
  @abstractmethod
  def append(self, id: str, values: Sequence[T], *, create: Literal[False]) -> Promise[Either[DBError|InexistentItem, None]]:
    """Appends `values` if it already existed. Otherwise doesn't append, and returns `Left[ExistentItem]`"""
  @overload
  @abstractmethod
  def append(self, id: str, values: Sequence[T], *, create: Literal[True] = True) -> Promise[Either[DBError, None]]:
    """Appends `values` to `id`, creating the item if needed"""

class AppendableKV(KV[Sequence[T]], Appendable[T], Generic[T]):
  ...
  
class SimpleAppendKV(AppendableKV[T], SimpleKV[Sequence[T]], Generic[T]):

  @P.lift
  async def append(self, id: str, values: Sequence[T], *, create: bool = True) -> Either[DBError|InexistentItem, None]: # type: ignore
    if not id in self.xs:
      if create:
        self.xs[id] = list(values)
      else:
        return Left(InexistentItem(id))
    else:
      self.xs[id].extend(values) # type: ignore
    return Right(None)