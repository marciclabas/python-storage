from typing import TypeVar, Callable
from sqlalchemy.types import TypeDecorator, String
from .meta import CustomTypeMeta

T = TypeVar('T')

class CustomStringMeta(type):
  def __new__(cls, name: str, bases, dct, dump: Callable[[T], str], parse: Callable[[str], T]) -> type[TypeDecorator[T]]:
    return CustomTypeMeta(name, bases, dct, String, dump=dump, parse=parse)
  
def CustomString(name: str, dump: Callable[[T], str], parse: Callable[[str], T]) -> type[TypeDecorator[T]]:
  return CustomTypeMeta(name, (), {}, String, dump=dump, parse=parse)

class SpaceDelimitedList(metaclass=CustomStringMeta, dump=' '.join, parse=str.split):
  ...