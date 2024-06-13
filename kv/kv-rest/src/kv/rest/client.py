from typing import TypeVar, Generic, Any, Literal, AsyncIterable, Sequence, Callable
from pydantic import TypeAdapter, RootModel
import httpx
from haskellian import either as E, Either, Left, Right
from kv.api import KV, InvalidData, ReadError, DBError

A = TypeVar('A')
ErrType = TypeAdapter(ReadError)
SeqType = TypeAdapter(Sequence[str])

def validate_left(raw_json: bytes) -> Left[DBError, Any]:
  try:
    return Left(ErrType.validate_json(raw_json))
  except Exception as e:
    return Left(DBError(e))
  
def validate_seq(raw_json: bytes) -> Either[DBError, Sequence[str]]:
  try:
    return Right(SeqType.validate_json(raw_json))
  except Exception as e:
    return Left(DBError(e))

class ClientKV(KV[A], Generic[A]):
  def __init__(
    self, endpoint: str, *,
    parse: Callable[[bytes], Either[InvalidData, A]] = Right, # type: ignore
    dump: Callable[[A], bytes|str] = lambda x: x # type: ignore
  ):
    self.endpoint = endpoint
    self.parse = parse
    self.dump = dump

  @classmethod
  def validated(cls, Type: type[A], endpoint: str) -> 'ClientKV[A]':
    Model = RootModel[Type]
    return ClientKV(
      endpoint=endpoint,
      parse=lambda b: E.validate_json(b, Model).fmap(lambda x: x.root).mapl(InvalidData),
      dump=lambda x: Model(x).model_dump_json(exclude_none=True)
    )
  
  async def _req(self, method: Literal['GET', 'POST', 'DELETE'], path: str, data: bytes | str | None = None):
    try:
      async with httpx.AsyncClient() as client:
        r = await client.request(method, f"{self.endpoint}/{path}", data=data) # type: ignore
        return Right(r.content) if r.status_code == 200 else validate_left(r.content)
    except Exception as e:
      return Left(DBError(e))

  async def _read(self, key: str):
    r = await self._req('GET', f'read?key={key}')
    return r.bind(self.parse)
  
  async def _insert(self, key: str, value: A):
    r = await self._req('POST', f'insert?key={key}', data=self.dump(value))
    return r.fmap(lambda _: None)
    
  async def _delete(self, key: str):
    r = await self._req('DELETE', f'delete?key={key}')
    return r.fmap(lambda _: None)

  async def _items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError | InvalidData, tuple[str, A]]]:
    keys = await self._keys()
    if keys.tag == 'left':
      yield Left(keys.value)
    else:
      for key in keys.value:
        val = await self._read(key)
        yield val.fmap(lambda v: (key, v))

  async def _keys(self) -> Either[DBError, Sequence[str]]:
    r = await self._req('GET', 'keys')
    return r.bind(validate_seq)    

