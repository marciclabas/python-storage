from typing import TypeVar, Sequence, Callable
import asyncio
from haskellian import Either, Left
from q.api import ReadQueue, ReadError, QueueError
from fastapi import FastAPI, Response, status as st
from fastapi.responses import JSONResponse

T = TypeVar('T')
U = TypeVar('U')

def read_api(
  queue: ReadQueue[T], *, timeout: int = 15,
  dump: Callable[[T], bytes|str] = lambda x: x # type: ignore
) -> FastAPI:
  """
  - `timeout`: timeout for read operations.
  """

  from .util import status
  app = FastAPI(generate_unique_id_function=lambda route: route.name)

  @app.get('/read/any')
  async def read_any():
    try:
      async with asyncio.timeout(timeout):
        e = await queue.read()
        if e.tag == 'right':
          k, _ = e.value
          return Response(k)
        else:
          return JSONResponse(content=e.value, status_code=status(e))
    except asyncio.TimeoutError:
      return Response('Timed out', status_code=st.HTTP_408_REQUEST_TIMEOUT)
    
  @app.get('/read')
  async def read(id: str, remove: bool = False):
    e = await queue._read(id, remove)
    if e.tag == 'right':
      _, v = e.value
      return Response(dump(v))
    else:
      return JSONResponse(content=e.value, status_code=status(e))
    
  
  @app.get('/keys')
  async def keys() -> Sequence[Either[ReadError, str]]:
    return await queue.keys().sync()

  return app