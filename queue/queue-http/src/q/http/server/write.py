from typing import TypeVar, Callable, overload
from q.api import WriteQueue, QueueError
from fastapi import FastAPI, Request
from haskellian import either as E, Either, Right, Left

T = TypeVar('T')

@overload
def write_api(
  queue: WriteQueue[T], *,
  parse: Callable[[bytes], Either[QueueError, T]] = Right
) -> FastAPI:
  ...
@overload
def write_api(
  queue: WriteQueue[T], *, Type: type[T]
) -> FastAPI:
  ...
def write_api(queue, *, parse = Right, Type = None): # type: ignore
  if Type is not None:
    from pydantic import TypeAdapter
    Adapter = TypeAdapter(Type)
    def parse(x):
      try:
        return Right(Adapter.validate_json(x))
      except Exception as e:
        return Left(QueueError(str(e)))
  
  return _write_api(queue, parse=parse)
  
def _write_api(
  queue: WriteQueue[T], *,
  parse: Callable[[bytes], Either[QueueError, T]] = Right
) -> FastAPI:

  from .util import with_status
  app = FastAPI(generate_unique_id_function=lambda route: route.name)

  @app.post('/push')
  @with_status
  @E.do[QueueError]()
  async def push(key: str, req: Request):
    body = await req.body()
    val = parse(body).unsafe()
    return (await queue.push(key, val)).unsafe()

  return app