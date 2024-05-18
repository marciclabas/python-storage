from typing import TypeVar, Generic, Callable, ParamSpec, Awaitable, Never, Sequence, AsyncIterable
from functools import wraps
from dataclasses import dataclass
from haskellian import either as E, Either, Left, Right, asyn_iter as AI
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import ContainerClient
from kv.api import DBError, InvalidData, InexistentItem, LocatableKV
from .util import blob_url

A = TypeVar('A')
Ps = ParamSpec('Ps')

def azure_safe(coro: Callable[Ps, Awaitable[A]]) -> Callable[Ps, Awaitable[Either[DBError, A]]]:
  @E.do()
  @wraps(coro)
  async def wrapper(*args: Ps.args, **kwargs: Ps.kwargs) -> A:
    try:
      return await coro(*args, **kwargs)
    except ResourceNotFoundError as e:
      Left(InexistentItem(detail=e)).unsafe()
    except Exception as e:
      Left(DBError(e)).unsafe()
    return Never
  return wrapper

@dataclass
class BlobContainerKV(LocatableKV[A], Generic[A]):
  """Key-Value store using a single Azure Blob Container. Keys must be valid blob names"""

  @classmethod
  def validated(cls, Type: type[A], client: Callable[[], ContainerClient]) -> 'BlobContainerKV[A]':
    from pydantic import RootModel
    Model = RootModel[Type]
    return BlobContainerKV(
      client=client,
      parse=lambda b: E.validate_json(b, Model).fmap(lambda x: x.root).mapl(InvalidData),
      dump=lambda x: Model(x).model_dump_json(exclude_none=True)
    )

  client: Callable[[], ContainerClient]
  parse: Callable[[bytes], Either[InvalidData, A]] = Right # type: ignore
  dump: Callable[[A], bytes | str] = lambda x: x # type: ignore

  @azure_safe
  async def _read(self, key: str):
    async with self.client() as client:
      r = await client.download_blob(key)
      data = await r.readall()
      return self.parse(data).unsafe()

  @azure_safe
  async def _insert(self, key: str, value: A):
    async with self.client() as client:
      if not await client.exists():
        await client.create_container()
      await client.upload_blob(key, self.dump(value), overwrite=True)

  @azure_safe
  async def _has(self, key: str) -> bool:
    async with self.client() as client:
      return await client.get_blob_client(key).exists()

  @azure_safe
  async def _delete(self, key: str):
    async with self.client() as client:
      await client.delete_blob(key)
  
  @azure_safe
  async def _keys(self) -> Sequence[str]:
    async with self.client() as client:
      return await AI.syncify(client.list_blob_names())

  async def _items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError, tuple[str, A]]]:
    keys = await self.keys()
    if keys.tag == 'left':
      yield Left(keys.value)
      return
    for key in keys.value:
      item = await self._read(key)
      if item.tag == 'left':
        yield Left(item.value)
      else:
        yield Right((key, item.value))

  def url(self, key: str) -> str:
    bc = self.client().get_blob_client(key)
    return blob_url(bc)