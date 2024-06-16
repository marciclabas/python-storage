from typing import Any
from haskellian import Left
from pydantic import TypeAdapter, ValidationError
from q.api import QueueError, ReadError

def urljoin(part1: str, part2: str):
  """What `urllib.parse.urljoin` ought to be."""
  return part1.rstrip('/') + '/' + part2.lstrip('/')

ErrType = TypeAdapter(ReadError)

def validate_left(raw_json: bytes, status: int) -> Left[QueueError, Any]:
  try:
    return Left(ErrType.validate_json(raw_json))
  except ValidationError:
    return Left(QueueError(f'Unexpected status code: {status}. Content: "{raw_json.decode()}"'))
  
