from typing import TypeVar, Generic, Callable, Literal
from haskellian import Either, Left, Right
from q.api import WriteQueue, QueueError
from .util import validate_left, urljoin
from .request import request, Request

T = TypeVar('T')

class WriteClientQ(WriteQueue[T], Generic[T]):

  def __init__(
    self, url: str, *,
    dump: Callable[[T], bytes] = lambda x: x, # type: ignore
    request: Request = request
  ):
    self.write_url = url
    self.dump = dump
    self.request = request

  @classmethod
  def validated(cls, Type: type[T], url: str, *, request: Request = request) -> 'WriteClientQ[T]':
    from pydantic import TypeAdapter
    dump = TypeAdapter(Type).dump_json
    return cls(url, dump=dump, request=request)


  async def _req(
      self, method: Literal['GET', 'POST', 'DELETE'], path: str, *,
      data: bytes | str | None = None, params: dict = {}
    ):
      try:
        r = await self.request(method, urljoin(self.write_url, path), data=data, params=params)
        return Right(r.content) if r.status_code == 200 else validate_left(r.content, r.status_code)
      except Exception as e:
        return Left(QueueError(e))
      
  async def push(self, key: str, value: T) -> Either[QueueError, None]:
    r = await self._req('POST', 'push', data=self.dump(value), params=dict(key=key))
    return r.fmap(lambda _: None).mapl(QueueError)