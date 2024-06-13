from typing import TypeVar, Callable
from q.api import WriteQueue, QueueError
from fastapi import FastAPI, Request
from haskellian import either as E, Either, Right

T = TypeVar('T')

def write_api(
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