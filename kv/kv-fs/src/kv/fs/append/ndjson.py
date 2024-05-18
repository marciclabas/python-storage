from typing_extensions import TypeVar, Sequence
from pydantic import RootModel, ValidationError
import haskellian.either as E

T = TypeVar('T')

def parse(data: str|bytes, Model: type[RootModel[T]]) -> E.Either[list[ValidationError], list[T]]:
  """Parses `data.splitlines()` into a list of models"""
  lines = data.splitlines()
  return E.sequence(
    E.validate_json(line, Model).fmap(lambda x: x.root)
    for line in lines
  )

def dump(items: Sequence[T], Model: type[RootModel[T]]) -> str:
  return '\n'.join(Model(item).model_dump_json(exclude_none=True) for item in items) + '\n'