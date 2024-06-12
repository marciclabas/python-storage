from typing import TypeVar, Sequence, Any, ParamSpec, Callable, Awaitable
from functools import wraps
import inspect
from fastapi import FastAPI, Response, status as st
from haskellian import Either, kwargs as kw
from kv.api import KV, DBError, ReadError

A = TypeVar('A')
Ps = ParamSpec('Ps')

def status(e: Either[ReadError, Any]):
  if e.tag == 'right':
    return st.HTTP_200_OK
  elif e.value.reason == 'db-error' or e.value.reason == 'invalid-data':
    return st.HTTP_500_INTERNAL_SERVER_ERROR
  else:
    return st.HTTP_404_NOT_FOUND

def with_status(func: Callable[Ps, Awaitable[Either[ReadError, A]]]):
  @wraps(func)
  async def wrapper(response: Response, *args: Ps.args, **kwargs: Ps.kwargs) -> Either[ReadError, A]:
    e = await func(*args, **kwargs)
    response.status_code = status(e)
    return e
  wrapper.__signature__ = kw.add_kw(inspect.signature(wrapper), 'response', Response) # type: ignore
  return wrapper

def fastapi(kv: KV[A]):

  app = FastAPI()

  @app.post('/insert')
  @with_status
  async def insert(key: str, value: A) -> Either[DBError, None]:
    return await kv.insert(key, value)
  
  @app.get('/read')
  @with_status
  async def read(key: str) -> Either[ReadError, A]:
    return await kv.read(key)
  
  @app.get('/has')
  @with_status
  async def has(key: str) -> Either[DBError, bool]:
    return await kv.has(key)
  
  @app.get('/keys')
  @with_status
  async def keys() -> Either[DBError, Sequence[str]]:
    return await kv.keys()
  
  @app.get('/values')
  async def values() -> Sequence[Either[ReadError, A]]:
    return await kv.values().sync()
  
  @app.get('/items')
  async def items() -> Sequence[Either[ReadError, tuple[str, A]]]:
    return await kv.items().sync()
  
  @app.delete('/delete')
  @with_status
  async def delete(key: str) -> Either[ReadError, None]:
    return await kv.delete(key)
  
  return app