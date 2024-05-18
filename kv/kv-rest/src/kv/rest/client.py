from typing import TypeVar, Generic, Any, Literal, AsyncIterable, Sequence
from pydantic import RootModel
import httpx
from haskellian import either as E, Either, Left, Right, Thunk
from kv.api import KV, InvalidData, ReadError, DBError

A = TypeVar('A')
Root = TypeVar('Root', bound=RootModel)

def root_validate(x: Any, Model: type[Root]) -> Either[InvalidData, Root]:
  return E.validate(x, Model).mapl(InvalidData)

class ClientKV(KV[A], Generic[A]):
  def __init__(self, endpoint: str, Type: type[A]):
    self.endpoint = endpoint
    self.client = httpx.AsyncClient()
    self.ReadModel = Thunk(lambda: RootModel[Either[ReadError, Type]])
    self.DBErrModel = Thunk(lambda: RootModel[Either[DBError, None]])
    self.Model = Thunk(lambda: RootModel[Type])
    self.ItemsModel = Thunk(lambda: RootModel[Sequence[Either[DBError, tuple[str, Type]]]])
    self.KeysModel = Thunk(lambda: RootModel[Either[DBError, Sequence[str]]])
  
  def __del__(self):
    import asyncio
    asyncio.create_task(self.client.aclose())

  async def _req(self, method: Literal['GET', 'POST', 'DELETE'], path: str, json = None):
    try:
      r = await self.client.request(method, f"{self.endpoint}/{path}", json=json)
      return Right(r.json())
    except Exception as e:
      return Left(DBError(e))

  @E.do[ReadError]()
  async def _read(self, key: str):
    r = (await self._req('GET', f'read?key={key}')).unsafe()
    return root_validate(r, self.ReadModel.get()).unsafe().root.unsafe()
  
  @E.do[DBError]()
  async def _insert(self, key: str, value: A):
    r = (await self._req('POST', f'insert?key={key}', json=self.Model.get()(value).model_dump())).unsafe()
    return root_validate(r, self.DBErrModel.get()).unsafe().root.unsafe()
    
  @E.do[DBError]()
  async def _delete(self, key: str):
    r = (await self._req('DELETE', f'delete?key={key}')).unsafe()
    return root_validate(r, self.DBErrModel.get()).unsafe().root.unsafe()

  async def _items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError | InvalidData, tuple[str, A]]]:
    r = await self._req('GET', 'items')
    if r.tag == 'left':
      yield Left(r.value)
      return
    items = root_validate(r.value, self.ItemsModel.get())
    if items.tag == 'left':
      yield Left(items.value)
      return
    for it in items.value.root:
      yield it

  @E.do[DBError]()
  async def _keys(self) -> Sequence[str]:
    r = (await self._req('GET', 'keys')).unsafe()
    return root_validate(r, self.KeysModel.get()).unsafe().root.unsafe()
