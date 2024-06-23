from typing_extensions import TypeVar, Generic, AsyncIterable, Sequence, Awaitable
from abc import ABC, abstractmethod
from haskellian import Either, Left, Right, IsLeft, promise as P, AsyncIter, either as E
from .errors import InexistentItem, DBError, InvalidData, ReadError

T = TypeVar('T')

class KV(ABC, Generic[T]):

  @classmethod
  def of(cls, conn_str: str, type: type[T] | None = None) -> 'KV[T]':
    """Create a KV from a connection string. Supports:
    - `file://<path>`: `FilesystemKV`
    - `sql+<protocol>://<conn_str>;Table=<table>`: `SQLKV`
    - `azure+blob://<conn_str>`: `BlobKV`
    - `azure+blob+container://<conn_str>;Container=<container_name>`: `BlobContainerKV`
    - `https://<endpoint>` (or `http://<endpoint>`): `ClientKV`
    """
    from .conn_strings import parse
    return parse(conn_str, type)
  
  @abstractmethod
  def _insert(self, key: str, value: T) -> Awaitable[Either[DBError, None]]: ...

  @P.lift
  async def insert(self, key: str, value: T):
    return await self._insert(key, value)

  @abstractmethod
  def _read(self, key: str) -> Awaitable[Either[ReadError, T]]: ...

  @P.lift
  async def read(self, key: str):
    return await self._read(key)

  @abstractmethod
  def _delete(self, key: str) -> Awaitable[Either[DBError | InexistentItem, None]]: ...

  @P.lift
  async def delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    return await self._delete(key)

  @abstractmethod
  def _items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError | InvalidData, tuple[str, T]]]: ...

  def items(self, batch_size: int | None = None) -> AsyncIter[Either[DBError | InvalidData, tuple[str, T]]]:
    return AsyncIter(self._items(batch_size))

  @P.lift
  async def has(self, key: str) -> Either[DBError, bool]:
    return (await self.keys()).fmap(lambda keys: key in keys)
  
  @abstractmethod
  def _keys(self) -> Awaitable[Either[DBError, Sequence[str]]]:
    ...

  @P.lift
  async def keys(self) -> Either[DBError, Sequence[str]]:
    return await self._keys()

  async def _values(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError|InvalidData, T]]:
    async for e in self.items(batch_size):
      yield e.fmap(lambda it: it[1])

  def values(self, batch_size: int | None = None) -> AsyncIter[Either[DBError|InvalidData, T]]:
    return AsyncIter(self._values(batch_size))

  async def _copy(self, key: str, to: 'KV[T]', to_key: str) -> Either[DBError|InexistentItem, None]:
    try:
      value = (await self.read(key)).unsafe()
      return await to.insert(to_key, value)
    except IsLeft as e:
      return Left(e.value)
    
  @P.lift
  async def copy(self, key: str, to: 'KV[T]', to_key: str) -> Either[DBError|InexistentItem, None]:
    return await self._copy(key, to, to_key)

  async def _move(self, key: str, to: 'KV[T]', to_key: str) -> Either[DBError|InexistentItem, None]:
    try:
      (await self._copy(key, to, to_key)).unsafe()
      (await self.delete(key)).unsafe()
      return Right(None)
    except IsLeft as e:
      return Left(e.value)

  @P.lift
  async def move(self, key: str, to: 'KV[T]', to_key: str) -> Either[DBError|InexistentItem, None]:
    return await self._move(key, to, to_key)

  @E.do[DBError]()
  async def _clear(self):
    keys = (await self.keys()).unsafe()
    for key in keys:
      (await self.delete(key)).unsafe()

  @P.lift
  async def clear(self):
    return await self._clear()