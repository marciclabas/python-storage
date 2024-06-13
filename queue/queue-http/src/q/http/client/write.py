from typing import TypeVar, Generic, Callable
from haskellian import Either
from q.api import WriteQueue, QueueError
from .util import request, urljoin

T = TypeVar('T')

class WriteClientQ(WriteQueue[T], Generic[T]):

  def __init__(
    self, url: str, *,
    dump: Callable[[T], bytes] = lambda x: x # type: ignore
  ):
    self.write_url = url
    self.dump = dump

  @classmethod
  def validated(cls, Type: type[T], url: str) -> 'WriteClientQ[T]':
    from pydantic import TypeAdapter
    dump = TypeAdapter(Type).dump_json
    return cls(url, dump=dump)

  async def push(self, key: str, value: T) -> Either[QueueError, None]:
    url = urljoin(self.write_url, 'push')
    r = await request(url, 'POST', data=self.dump(value), params=dict(key=key))
    return r.fmap(lambda _: None).mapl(QueueError)