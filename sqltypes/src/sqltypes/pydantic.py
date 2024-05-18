from typing import TypeVar, Generic
from sqlalchemy.types import TypeDecorator, JSON
from pydantic import BaseModel
from .meta import CustomTypeMeta

M = TypeVar('M', bound=BaseModel)

class PydanticModel(type):
  def __new__(cls, Model: type[M], name: str | None = None) -> type[TypeDecorator[M]]:
    return CustomTypeMeta(f'DB{name or Model.__name__}', (), {}, JSON, dump=lambda M: M.model_dump(exclude_none=True), parse=Model.model_validate)
