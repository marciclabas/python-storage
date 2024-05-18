from typing_extensions import Generic, TypeVar, Sequence
import os
from pydantic import RootModel
from haskellian import either as E, promise as P
from kv.api import AppendableKV, InexistentItem, DBError, InvalidData
import fs
from ..api import FilesystemKV
from . import ndjson

A = TypeVar('A')
T = TypeVar('T')

class FilesystemAppendKV(FilesystemKV[Sequence[T]], AppendableKV[T], Generic[T]):

  @P.lift
  async def append(self, id: str, values: Sequence[T], *, create: bool = True): # type: ignore
    if not create and not os.path.exists(self._path(id)):
      return E.Left(InexistentItem(id))
    either = fs.append(self._path(id), self.dump(values))
    return either.mapl(self._parse_err) # type: ignore
    
  @classmethod
  def validated(cls, Type: type[A], base_path: str) -> 'FilesystemAppendKV[A]': # type: ignore
    Model = RootModel[Type]
    return FilesystemAppendKV(
      base_path=base_path, extension='.ndjson',
      parse=lambda data: ndjson.parse(data, Model).mapl(InvalidData),
      dump=lambda items: ndjson.dump(items, Model)
    )
  