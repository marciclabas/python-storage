from typing_extensions import Generic, TypeVar
from .read import ReadQueue
from .write import WriteQueue

A = TypeVar('A')

class Queue(ReadQueue[A], WriteQueue[A], Generic[A]):
  ...