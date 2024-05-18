from typing_extensions import Literal, Any
from dataclasses import dataclass

class StrMixin:
  def __str__(self) -> str:
    return self.__repr__()

@dataclass(eq=False)
class QueueError(StrMixin, BaseException):
  detail: Any | None = None
  reason: Literal['queue-error'] = 'queue-error'

@dataclass(eq=False)
class InexistentItem(StrMixin, BaseException):
  key: str | None = None
  detail: Any | None = None
  reason: Literal['inexistent-item'] = 'inexistent-item'
  
ReadError = QueueError | InexistentItem