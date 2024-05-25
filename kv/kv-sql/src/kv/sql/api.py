from typing_extensions import AsyncIterable, Sequence, TypeVar, Generic
from pydantic import RootModel
from haskellian import Either, Left, Right
from sqlmodel import Session, select
from sqlalchemy import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import DatabaseError
from sqltypes import PydanticModel
from kv.api import KV
from kv.api import DBError, InexistentItem, InvalidData

T = TypeVar('T')

class SQLKV(KV[T], Generic[T]):
  """Key-Value implementation over sqlalchemy"""
  
  def __init__(self, Type: type[T], engine: Engine, table: str = 'kv'):
    self.Type = RootModel[Type]
    self.engine = engine

    class Base(DeclarativeBase):
      ...

    class Table(Base):
      __tablename__ = table
      key: Mapped[str] = mapped_column(primary_key=True)
      value: Mapped[RootModel[Type]] = mapped_column(type_=PydanticModel(self.Type))

    self.Table = Table
    Base.metadata.create_all(engine)

  async def _delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    try:
      with Session(self.engine) as session:
        stmt = select(self.Table).where(self.Table.key == key)
        row = session.exec(stmt).first()
        if row is None:
          return Left(InexistentItem(key))
        session.delete(row)
        session.commit()
        return Right(None)
    except DatabaseError as e:
      return Left(DBError(e))

  async def _read(self, key: str) -> Either[DBError | InvalidData | InexistentItem, T]:
    try:
      with Session(self.engine) as session:
        stmt = select(self.Table).where(self.Table.key == key)
        row = session.exec(stmt).first()
        if row is None:
          return Left(InexistentItem(key))
        return Right(row.value.root)
    except DatabaseError as e:
      return Left(DBError(e))

  async def _insert(self, key: str, value: T) -> Either[DBError, None]:
    try:
      with Session(self.engine) as session:
        stmt = select(self.Table).where(self.Table.key == key)
        row = session.exec(stmt).first()
        if row is not None:
          session.delete(row)
        session.add(self.Table(key=key, value=self.Type(value)))
        session.commit()
        return Right(None)
    except DatabaseError as e:
      return Left(DBError(e))

  async def _keys(self) -> Either[DBError, Sequence[str]]:
    try:
      with Session(self.engine) as session:
        stmt = select(self.Table.key)
        return Right(session.exec(stmt).all())
    except DatabaseError as e:
      return Left(DBError(e))

  async def _items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError | InvalidData, tuple[str, T]]]:
    try:
      with Session(self.engine) as session:
        result = session.exec(select(self.Table))
        while (batch := result.fetchmany(batch_size)) != []:
          for row in batch:
            yield Right((row.key, row.value.root))
    except DatabaseError as e:
      yield Left(DBError(e))