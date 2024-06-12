from typing import TypeVar, Generic, AsyncIterable, Sequence
from pydantic import RootModel
import httpx
from haskellian import Either, Left, Thunk, asyn_iter as AI
from q.api import ReadQueue, ReadError, QueueError

T = TypeVar('T')

async def safe_get(url: str, params: dict | None = None):
  try:
    async with httpx.AsyncClient() as client:
      r = await client.get(url, params=params)
      return r.json()
  except Exception as e:
    return Left(QueueError(str(e)))
  
def safe_validate(itemsponse, Root: type[RootModel]):
  try:
    return Root.model_validate(itemsponse).root
  except Exception as e:
    return Left(QueueError(str(e)))
  

class ReadClientQ(ReadQueue[T], Generic[T]):
    
  def __init__(self, Type: type[T], url: str):
    self.read_url = url
    self.ReadModel = Thunk(lambda: RootModel[Either[ReadError, tuple[str, Type]]])
    self.ItemsModel = Thunk(lambda: RootModel[Sequence[Either[ReadError, tuple[str, Type]]]])
    self.KeysModel = Thunk(lambda: RootModel[Sequence[Either[ReadError, str]]])

  async def _read(self, id: str | None, remove: bool) -> Either[ReadError, tuple[str, T]]:
    params: dict = { 'remove': remove }
    if id:
      params['id']
    r = await safe_get(f'{self.read_url}/read', params)
    return safe_validate(r, self.ReadModel())
    
  async def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, T]]]:
    r = await safe_get(f'{self.read_url}/items')
    items = safe_validate(r, self.ItemsModel())
    if isinstance(items, Left):
      yield items
      return
    for item in items:
      yield item # type: ignore

  @AI.lift
  async def keys(self) -> AsyncIterable[Either[ReadError, str]]:
    r = await safe_get(f'{self.read_url}/keys')
    items = safe_validate(r, self.KeysModel())
    if isinstance(items, Left):
      yield items
      return
    for item in items:
      yield item # type: ignore