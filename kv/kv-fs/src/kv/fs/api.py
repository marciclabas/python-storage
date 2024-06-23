from typing_extensions import TypeVar, Generic, Callable, AsyncIterable, Never, Sequence
from dataclasses import dataclass
import os
from haskellian import either as E, Right, Left, Either
from pydantic import RootModel
from kv.api import KV, LocatableKV, InexistentItem, InvalidData, DBError
import fs

A = TypeVar('A')
T = TypeVar('T')

@dataclass
class FilesystemKV(LocatableKV[T], Generic[T]):

  @classmethod
  def validated(cls, Type: type[A], base_path: str) -> 'FilesystemKV[A]':
    Model = RootModel[Type]
    return FilesystemKV(
      base_path=base_path, extension='.json',
      parse=lambda b: E.validate_json(b, Model).fmap(lambda x: x.root).mapl(InvalidData),
      dump=lambda x: Model(x).model_dump_json(exclude_none=True)
    )

  base_path: str
  extension: str | None = None
  parse: Callable[[bytes], E.Either[InvalidData, T]] = lambda x: E.Right(x) # type: ignore
  dump: Callable[[T], bytes|str] = lambda x: x # type: ignore
  
  def __post_init__(self):
    os.makedirs(self.base_path, exist_ok=True)

  def _path(self, key: str) -> str:
    return os.path.abspath(os.path.join(self.base_path, f'{key}{self.extension or ""}'))
  
  def url(self, id: str, *, expiry = None) -> str:
    return self._path(id)
  
  def _key(self, path: str) -> str:
    if self.extension is None:
      return path
    else:
      return os.path.splitext(path)[0]
  
  def _parse_err(self, key: str):
    def _curried(err: OSError) -> DBError | InexistentItem:
      match err:
        case FileNotFoundError():
          return InexistentItem(key, detail=f"File not found: {self._path(key)}")
        case OSError():
          return DBError(str(err))
    return _curried
    
  async def _insert(self, key: str, value: T) -> E.Either[DBError, None]:
    return fs.write(self._path(key), self.dump(value), replace=True) \
      .mapl(self._parse_err(key=key)) # type: ignore
  
  async def _read(self, key: str) -> E.Either[DBError | InvalidData | InexistentItem, T]:
    either = fs.read(self._path(key)) \
      .mapl(self._parse_err(key=key))
    return either.bind(self.parse) # type: ignore
  
  async def _delete(self, key: str) -> E.Either[DBError | InexistentItem, None]:
    return fs.delete(self._path(key)) \
      .mapl(self._parse_err(key=key)) # type: ignore
  
  async def _has(self, key: str) -> E.Right[Never, bool]:
    return Right(os.path.exists(self._path(key)))
  
  async def _keys(self) -> Right[Never, Sequence[str]]:
    return Right(fs.filenames(self.base_path).map(self._key).sync())
  
  async def _items(self, batch_size: int | None = None) -> AsyncIterable[E.Either[DBError | InvalidData, tuple[str, T]]]:
    for path in fs.filenames(self.base_path):
      key = self._key(path)
      yield (await self.read(key)).fmap(lambda value: (key, value)) # type: ignore

  async def _copy(self, key: str, to: 'KV[T]', to_key: str) -> E.Either[DBError|InexistentItem, None]:
    if not isinstance(to, FilesystemKV):
      return await super()._copy(key, to, to_key)
    
    match fs.copy(self._path(key), to._path(to_key)):
      case E.Right():
        return E.Right(None)
      case E.Left(FileNotFoundError()) as e:
        return E.Left(InexistentItem(key, detail=str(e.value)))
      case E.Left() as e:
        return E.Left(DBError(detail=str(e.value)))
 
  async def _move(self, key: str, to: 'KV[T]', to_key: str) -> E.Either[DBError|InexistentItem, None]:
    if not isinstance(to, FilesystemKV):
      return await super().move(key, to, to_key)
    
    match fs.move(self._path(key), to._path(to_key)):
      case E.Right():
        return E.Right(None)
      case E.Left(FileNotFoundError()) as e:
        return E.Left(InexistentItem(key, detail=str(e.value)))
      case E.Left() as e:
        return E.Left(DBError(detail=str(e.value)))
      
  async def _clear(self) -> Either[DBError, None]:
    from shutil import rmtree
    try:
      rmtree(self.base_path)
      return Right(None)
    except Exception as e:
      return Left(DBError(detail=str(e)))