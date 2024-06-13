from typing import TypeVar, Generic, AsyncIterable, Callable, Sequence
import asyncio
from datetime import timedelta
from pydantic import TypeAdapter
from haskellian import Either, Left, Right, asyn_iter as AI
import json
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
    polling_interval = timedelta(seconds=15),
  ):
    self.read_url = url
    self.parse = parse
    self.polling_interval = polling_interval

  @classmethod
  def validated(cls, Type: type[T], url: str, *, polling_interval = timedelta(seconds=15)) -> 'ReadClientQ[T]':
    from pydantic import TypeAdapter
    Adapter = TypeAdapter(Type)
    def parse(x):
      try:
        return Right(Adapter.validate_json(x))
      except Exception as e:
        return Left(QueueError(str(e)))
    return cls(url, parse=parse, polling_interval=polling_interval)


  async def _read(self, id: str | None, remove: bool) -> Either[ReadError, tuple[str, T]]: # type: ignore
    
    if id is None: # read/any -> returns an arbitrary id
      url = urljoin(self.read_url, 'read/any')
      r = await request(url, 'GET')
      if r.tag == 'left':
        if r.value.reason == 'inexistent-item':
          await asyncio.sleep(self.polling_interval.total_seconds())
          return await self._read(None, remove)

      id: str = json.loads(r.unsafe())

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
      yield r.mapl(QueueError)
    else:
      for key in validate_seq(r.value):
        yield key