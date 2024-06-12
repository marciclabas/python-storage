from typing import TypeVar, Generic
import httpx
from haskellian import Either, Left, Thunk
from q.api import WriteQueue, QueueError
from pydantic import TypeAdapter

T = TypeVar('T')

class WriteClientQ(WriteQueue[T], Generic[T]):

  def __init__(self, Type: type[T], url: str):
    self.write_url = url
    self.ReqModel = Thunk(lambda: TypeAdapter(Type))
    self.ResponseModel = TypeAdapter(Either[QueueError, None])

  async def push(self, key: str, value: T) -> Either[QueueError, None]:
    try:
      async with httpx.AsyncClient() as client:
        json = self.ReqModel().dump_python(value)
        r = await client.post(f'{self.write_url}/push/{key}', json=json)
        try:
          return self.ResponseModel.validate_python(r.json())
        except Exception as e:
          return Left(QueueError(e))
    except Exception as e:
      return Left(QueueError(e))