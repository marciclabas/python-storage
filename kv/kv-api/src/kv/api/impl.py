from typing_extensions import Awaitable, Generic, Sequence, TypeVar, AsyncIterable, Never
from haskellian import Left, Right, Either, either as E, promise as P, asyn_iter as AI
from .kv import KV
from .errors import InexistentItem, DBError, InvalidData, ReadError

T = TypeVar('T')

class SimpleKV(KV[T], Generic[T]):
  """Simple `KV` using a `dict`"""

  def __init__(self, items: dict[str, T] = {}):
    self.xs = items

  async def _insert(self, key: str, value: T) -> Right[Never, None]:
    self.xs[key] = value
    return Right(None)

  async def _has(self, key: str) -> Either[DBError, bool]:
    return Right(key in self.xs)

  async def _read(self, key: str) -> Either[ReadError, T]:
    return E.maybe(self.xs.get(key)).mapl(lambda _: InexistentItem(key))

  async def _delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    if not key in self.xs:
      return Left(InexistentItem(key))
    else:
      del self.xs[key]
      return Right(None)
    
  async def _keys(self) -> Either[DBError, Sequence[str]]:
    return Right(list(self.xs.keys()))

  async def _items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError | InvalidData, tuple[str, T]]]:
    for item in self.xs.items():
      yield Right(item)


SimpleKV()