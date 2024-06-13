from typing import TypeVar, Generic, AsyncIterable, Callable, Sequence
from pydantic import TypeAdapter
from haskellian import Either, Left, Right, asyn_iter as AI
from q.api import ReadQueue, ReadError, QueueError
from .util import request, urljoin

T = TypeVar('T')

KeysType = TypeAdapter(Sequence[Either[QueueError, str]])

def validate_seq(raw_json: bytes) -> Sequence[Either[QueueError, str]]:
  try:
    return KeysType.validate_json(raw_json)
  except Exception as e:
    return [Left(QueueError(e))]

  
class ReadClientQ(ReadQueue[T], Generic[T]):
    
  def __init__(
    self, url: str, *,
    parse: Callable[[bytes], Either[QueueError, T]] = Right,
  ):
    self.read_url = url
    self.parse = parse

  async def _read(self, id: str | None, remove: bool) -> Either[ReadError, tuple[str, T]]:
    
    if id is None: # read any -> returns an arbitrary id
      url = urljoin(self.read_url, 'read/any')
      r = await request(url, 'GET')
      if r.tag == 'left':
        return r
      id = r.unsafe().decode()

    url = urljoin(self.read_url, 'read')
    data = await request(url, 'GET', params=dict(id=id, remove=remove))
    return data.bind(self.parse).fmap(lambda val: (id, val))
    
  async def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, T]]]:
    keys = await self.keys().sync()
    for key in keys:
      if key.tag == 'left':
        yield Left(key.value)
      else:
        yield (await self._read(key.value, remove=False)).mapl(QueueError)

  @AI.lift
  async def keys(self) -> AsyncIterable[Either[QueueError, str]]:
    url = urljoin(self.read_url, 'keys')
    r = await request(url, 'GET')
    if r.tag == 'left':
      yield r
    else:
      for key in validate_seq(r.value):
        yield key