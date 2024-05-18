from typing_extensions import Generic, TypeVar
from abc import ABC, abstractmethod
from ..kv import KV

A = TypeVar('A')

class Locatable(ABC, Generic[A]):
  @abstractmethod
  def url(self, key: str, /) -> str:
    ...

class LocatableKV(KV[A], Locatable[A], Generic[A]):
  ...