from q.api.errors import QueueError
from typing_extensions import AsyncIterable, Generic, TypeVar, Never
from haskellian import Either, Left, Right, promise as P
from .. import ReadQueue, WriteQueue, InexistentItem

A = TypeVar('A')

class EmptyQueue(ReadQueue[A], WriteQueue[A], Generic[A]):

  async def _read(self, id: str | None, remove: bool) -> Either[InexistentItem, Never]:
    if id is None:
      await P.ManagedPromise() # will never resolve
      return Never
    else:
      return Left(InexistentItem(id, detail='This is an `EmptyQueue`'))
  
  async def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, A]]]:
    if False:
      yield
  
  async def push(self, key: str, value: A) -> Right[Never, None]:
    return Right(None)