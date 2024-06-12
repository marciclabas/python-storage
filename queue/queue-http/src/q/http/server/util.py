from typing import ParamSpec, TypeVar, Awaitable, Callable
from functools import wraps
import inspect
from fastapi import Response, status as st
from haskellian import Either, kwargs as kw
from q.api import ReadError

T = TypeVar('T')
Ps = ParamSpec('Ps')

def status(e: Either[ReadError, T]):
  if e.tag == 'right':
    return st.HTTP_200_OK
  elif e.value.reason == 'queue-error':
    return st.HTTP_500_INTERNAL_SERVER_ERROR
  else:
    return st.HTTP_404_NOT_FOUND

def with_status(func: Callable[Ps, Awaitable[Either[ReadError, T]]]):
  @wraps(func)
  async def wrapper(response: Response, *args: Ps.args, **kwargs: Ps.kwargs) -> Either[ReadError, T]:
    e = await func(*args, **kwargs)
    response.status_code = status(e)
    return e
  wrapper.__signature__ = kw.add_kw(inspect.signature(wrapper), 'response', Response) # type: ignore
  return wrapper