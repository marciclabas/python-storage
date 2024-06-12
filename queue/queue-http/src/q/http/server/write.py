from typing import TypeVar, Annotated
from q.api import WriteQueue
from fastapi import FastAPI, Body

T = TypeVar('T')

def write_api(queue: WriteQueue[T]) -> FastAPI:

  from .util import with_status
  app = FastAPI()

  @app.post('/push/{id}')
  @with_status
  async def push(id: str, value: Annotated[T, Body()]):
    return await queue.push(id, value)

  return app