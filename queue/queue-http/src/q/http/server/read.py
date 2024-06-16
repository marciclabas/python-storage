from typing import TypeVar, Sequence, Callable, overload
from haskellian import Either, Left
from q.api import ReadQueue, ReadError, InexistentItem
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter

T = TypeVar('T')
U = TypeVar('U')

@overload
def read_api(
  queue: ReadQueue[T], *,
  dump: Callable[[T], bytes|str] = lambda x: x # type: ignore
) -> FastAPI:
  ...
@overload
def read_api(
  queue: ReadQueue[T], *, Type: type[T]
) -> FastAPI:
  ...
def read_api(queue, *, dump = lambda x: x, Type = None): # type: ignore
  if Type is not None:
    from pydantic import TypeAdapter
    dump = TypeAdapter(Type).dump_json
  
  return _read_api(queue, dump=dump)

def _read_api(
  queue: ReadQueue[T], *,
  dump: Callable[[T], bytes|str] = lambda x: x # type: ignore
) -> FastAPI:
  """
  - `timeout`: timeout for read operations.
  """

  from .util import status, with_status
  app = FastAPI(generate_unique_id_function=lambda route: route.name)

  @app.get('/read/any')
  @with_status
  async def read_any():
    async for e in queue.keys():
      if e.tag == 'right':
        return e
    
    return Left(InexistentItem(detail='No keys found'))

  @app.get('/read')
  async def read(id: str, remove: bool = False):
    e = await queue._read(id, remove)
    if e.tag == 'right':
      _, v = e.value
      return Response(dump(v))
    else:
      content = TypeAdapter(ReadError).dump_json(e.value)
      return Response(content, status_code=status(e))
    
  
  @app.get('/keys')
  async def keys() -> Sequence[Either[ReadError, str]]:
    return await queue.keys().sync()

  return app