from typing import TypeVar, Callable
from pydantic import BaseModel
from sqlalchemy.types import TypeDecorator, TypeEngine

T = TypeVar('T')
D = TypeVar('D')
E = TypeVar('E', bound=TypeEngine)
M = TypeVar('M', bound=BaseModel)

class CustomTypeMeta(type):
  def __new__(cls, name: str, bases: tuple, dct: dict, Impl: type[E], dump: Callable[[T], D], parse: Callable[[D], T]):
    
    class CustomType(TypeDecorator):
      impl = Impl
      cache_ok = True

      def process_bind_param(self, value: T | None, dialect) -> D | None:
        if value is not None:
          return dump(value)

      def process_result_value(self, value: D | None, dialect) -> T | None:
        if value is not None:
          return parse(value)

    # Return the new class type
    return type(name, (CustomType, *bases), dct)
