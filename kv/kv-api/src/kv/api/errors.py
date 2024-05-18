from typing_extensions import Literal, Any
from dataclasses import dataclass

class StrMixin:
  def __str__(self) -> str:
    return self.__repr__()

@dataclass(eq=False)
class InexistentItem(StrMixin, BaseException):
  key: str | None = None
  detail: Any | None = None
  reason: Literal['inexistent-item'] = 'inexistent-item'

@dataclass(eq=False)
class DBError(StrMixin, BaseException):
  detail: Any = None
  reason: Literal['db-error'] = 'db-error'

@dataclass(eq=False)
class InvalidData(StrMixin, BaseException):
  detail: Any = None
  reason: Literal['invalid-data'] = 'invalid-data'

ReadError = DBError | InvalidData | InexistentItem