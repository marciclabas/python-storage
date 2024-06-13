from typing import Literal, Any
from haskellian import Left, Right
import httpx
from pydantic import TypeAdapter
from q.api import QueueError, ReadError

def urljoin(part1: str, part2: str):
  """`urllib.parse.urljoin` is plain dumb. This is what works."""
  return part1.rstrip('/') + '/' + part2.lstrip('/')

ErrType = TypeAdapter(ReadError)

def validate_left(raw_json: bytes) -> Left[QueueError, Any]:
  try:
    return Left(ErrType.validate_json(raw_json))
  except Exception as e:
    return Left(QueueError(e))
  
async def request(
  url: str, method: Literal['GET', 'POST', 'DELETE'], *,
  data: bytes | str | None = None, params: dict | None = None
):
    try:
      async with httpx.AsyncClient() as client:
        r = await client.request(method, url, data=data, params=params) # type: ignore
        return Right(r.content) if r.status_code == 200 else validate_left(r.content)
    except Exception as e:
      return Left(QueueError(e))
    