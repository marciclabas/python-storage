from typing_extensions import Generic, TypeVar, Sequence
from haskellian import Either, Left
from kv.api import AppendableKV, InexistentItem as KVInexistentItem
import kv.fs
from q.api import AppendableQueue, InexistentItem, ReadError, QueueError
from .api import QueueKV

A = TypeVar('A')
T = TypeVar('T')

class AppendQueueKV(QueueKV[Sequence[T]], AppendableQueue[T], Generic[T]):

  def __init__(self, kv: AppendableKV[T]):
    super().__init__(kv)
    self._kv = kv
  
  @classmethod
  def fs(cls, Type: type[A], path: str) -> 'AppendQueueKV[A]': # type: ignore
    return AppendQueueKV[A](kv.fs.FilesystemAppendKV.validated(Type, path))

  async def append(self, id: str, values: Sequence[T], *, create: bool = False) -> Either[ReadError, None]: # type: ignore
    match await self._kv.append(id, values, create=create):
      case Left(KVInexistentItem()):
        return Left(InexistentItem())
      case either:
        return either.mapl(QueueError)
  