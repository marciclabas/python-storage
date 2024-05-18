from typing_extensions import AsyncIterable, Generic, Literal, TypeVar, overload
import asyncio
import os
from datetime import timedelta
from haskellian import either as E, AsyncIter, iter as I, Either, Left, IsLeft, Right
from kv.api import KV, InexistentItem as KVInexistentItem
from q.api import Queue, QueueError, ReadError, InexistentItem

A = TypeVar('A')
B = TypeVar('B')

class QueueKV(Queue[A], Generic[A]):

  def __init__(
    self, kv: KV[A],
    poll_interval: timedelta = timedelta(seconds=5),
  ):
    self._kv = kv
    self.poll_interval = poll_interval

  @classmethod
  def fs(cls, Type: type[B], path: str) -> 'QueueKV[B]':
    try:
      from kv.fs import FilesystemKV
    except ImportError:
      raise ImportError('Install `kv-fs` to run in filesystem')
    return QueueKV(FilesystemKV.validated(Type, path))
  
  @classmethod
  def sqlite(cls, Type: type[B], path: str, table: str = 'queue') -> 'QueueKV[B]':
    try:
      from kv.sqlite import SQLiteKV
    except ImportError:
      raise ImportError('Install `kv-sqlite-sync` to run in local SQLite')
    if len(os.path.basename(path).split('.')) == 1:
      path += '.sqlite'
    return QueueKV(SQLiteKV.validated(Type, path, table))
  
  @classmethod
  @overload
  def at(cls, Type: type[B], path: str, protocol: Literal['fs']) -> 'QueueKV[B]': ...
  @classmethod
  @overload
  def at(cls, Type: type[B], path: str, protocol: Literal['sqlite'], table: str = 'queue') -> 'QueueKV[B]': ...
  
  @classmethod
  def at(cls, Type: type[B], path: str, protocol: Literal['fs', 'sqlite'], table: str = 'queue') -> 'QueueKV[B]':
    return QueueKV.fs(Type, path) if protocol == 'fs' else QueueKV.sqlite(Type, path, table)


  async def push(self, key: str, value: A):
    return (await self._kv.insert(key, value)).mapl(QueueError)
  
  async def _read(self, id: str | None = None, remove: bool = False) -> Either[ReadError, tuple[str, A]]:
    if id is None:
      key = I.head((await self._kv.keys()).unsafe())
      if key is None:
        await asyncio.sleep(self.poll_interval.total_seconds())
        return await self._read(id, remove)
    else:
      key = id
    
    try:
      value = (await self._kv.read(key)).unsafe()
      if remove:
        (await self._kv.delete(key)).unsafe()
      return Right((key, value))
    except IsLeft as e:
      match e.value:
        case KVInexistentItem():
          return Left(InexistentItem(key))
        case err:
          return Left(err)
    
  def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, A]]]:
    return self._kv.items().map(lambda e: e.mapl(QueueError))
  