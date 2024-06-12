from typing import TypeVar, Sequence
import asyncio
from haskellian import Either, Left
from q.api import ReadQueue, ReadError, QueueError
from fastapi import FastAPI

T = TypeVar('T')
U = TypeVar('U')

def read_api(queue: ReadQueue[T], *, timeout: int = 15) -> FastAPI:
  """
  - `timeout`: timeout for read operations.
  """

  from .util import with_status
  app = FastAPI()

  @app.get('/read')
  @with_status
  async def read(id: str | None = None, remove: bool = False) -> Either[ReadError, tuple[str, T]]:
    try:
      async with asyncio.timeout(timeout):
        return await queue._read(id, remove)
    except asyncio.TimeoutError:
      return Left(QueueError('Timed out'))
  
  @app.get('/keys')
  async def keys() -> Sequence[Either[ReadError, str]]:
    return await queue.keys().sync()
  
  @app.get('/values')
  async def values() -> Sequence[Either[ReadError, T]]:
    return await queue.values().sync()
  
  @app.get('/items')
  async def items() -> Sequence[Either[ReadError, tuple[str, T]]]:
    return await queue.items().sync()

  return app