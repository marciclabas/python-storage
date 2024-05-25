from typing_extensions import Generic, TypeVar
from abc import ABC, abstractmethod
from datetime import datetime
from ..kv import KV

A = TypeVar('A')

class Locatable(ABC, Generic[A]):
  @abstractmethod
  def url(self, key: str, /, *, expiry: datetime | None = None) -> str:
    ...

class LocatableKV(KV[A], Locatable[A], Generic[A]):
  ...