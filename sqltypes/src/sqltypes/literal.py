from sqlalchemy.types import TypeDecorator, String
from typing import TypeVar
from pydantic import RootModel
from .meta import CustomTypeMeta

S = TypeVar('S', bound=str)

class ValidatedLiteral(type):
  def __new__(cls, LiteralType: type[S]) -> type[TypeDecorator[S]]:
    Type = RootModel[LiteralType]
    def dump(x: S) -> str:
      Type.model_validate(x)
      return x
    def parse(x: str) -> S:
      Type.model_validate(x)
      return x # type: ignore
    return CustomTypeMeta(LiteralType.__name__, (), {}, String, dump=dump, parse=parse)