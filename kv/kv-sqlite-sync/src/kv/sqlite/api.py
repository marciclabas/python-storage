from typing_extensions import AsyncIterable, TypeVar, Generic, Callable, cast, Sequence
from dataclasses import dataclass
from haskellian import either as E, promise as P, asyn_iter as AI
from pydantic import RootModel
from kv.api import KV, InexistentItem, DBError, InvalidData
import sqlite3
import os
from . import queries

T = TypeVar('T')
M = TypeVar('M')

@dataclass
class SQLiteKV(KV[T], Generic[T]):

  conn: sqlite3.Connection
  table: str = 'kv'
  parse: Callable[[str], E.Either[InvalidData, T]] = lambda x: E.Right(cast(T, x))
  dump: Callable[[T], str] = str
  dtype: str = 'TEXT'

  @classmethod
  def at(
    cls, db_path: str, table: str = 'kv',
    parse: Callable[[str], E.Either[InvalidData, T]] = lambda x: E.Right(cast(T, x)),
    dump: Callable[[T], str] = str,
    dtype: str = 'TEXT'
  ) -> 'SQLiteKV[T]':
    dir = os.path.dirname(db_path)
    if dir != '':
      os.makedirs(dir, exist_ok=True)
    return SQLiteKV(sqlite3.connect(db_path), table, parse, dump, dtype)

  @classmethod
  def validated(cls, Type: type[M], db_path: str, table: str = 'kv') -> 'SQLiteKV[M]':
    Model = RootModel[Type]
    return cls.at(
      db_path=db_path, table=table, dtype='JSON',
      parse=lambda b: E.validate_json(b, Model).fmap(lambda x: x.root).mapl(InvalidData),
      dump=lambda x: Model(x).model_dump_json(exclude_none=True)
    )

  def __post_init__(self):
    self.conn.execute(*queries.create(self.table, self.dtype))

  def execute(self, query: queries.Query) -> E.Either[DBError, sqlite3.Cursor]:
    """Safely execute `query` on `self.conn`"""
    try:
      cur = self.conn.execute(*query)
      self.conn.commit()
      return E.Right(cur)
    except sqlite3.Error as err:
      return E.Left(DBError(str(err)))

  async def _insert(self, key: str, value: T) -> E.Either[DBError, None]:
    return self.execute(queries.upsert(key, self.dump(value), table=self.table)) | (lambda _: None)
  
  async def _has(self, key: str) -> E.Either[DBError, bool]:
    return self.execute(queries.read(key, table=self.table)).fmap(
      lambda cur: cur.fetchone() is not None
    )
    
  async def _read(self, key: str) -> E.Either[DBError | InvalidData | InexistentItem, T]:
    res = self.execute(queries.read(key, table=self.table)) \
      | sqlite3.Cursor.fetchone
    match res:
      case E.Right(None):
        return E.Left(InexistentItem(key))
      case E.Right([data]):
        return self.parse(data)
      case E.Right(bad_data):
        return E.Left(InvalidData(detail=f'Found invalid row: {bad_data}'))
      case err:
        return err

  async def _delete(self, key: str) -> E.Either[DBError | InexistentItem, None]:
    return self.execute(queries.delete(key, table=self.table)).bind(
      lambda cur: E.Left(InexistentItem(key)) if cur.rowcount == 0 else E.Right(None)
    )
  
  async def _keys(self) -> E.Either[DBError, Sequence[str]]:
    return self.execute(queries.keys(self.table)).fmap(
      lambda cur: [key for [key] in cur.fetchall()]
    )

  async def _items(self, batch_size: int | None = None) -> AsyncIterable[E.Either[DBError | InvalidData, tuple[str, T]]]:
    match self.execute(queries.items(self.table)):
      case E.Right(cur):
        while (batch := cur.fetchmany(batch_size or 256)) != []:
          for k, v in batch:
            yield self.parse(v) | (lambda v: (k, v))
      case E.Left(err):
        yield E.Left(err)
  