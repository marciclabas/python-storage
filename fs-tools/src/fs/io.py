import os
from pathlib import Path
from haskellian import Either, Left, Right, either as E
from .paths import ensure_path

def append(path: str | Path, data: str | bytes) -> Either[OSError, None]:
  """Append `data` to file at `path`"""
  mode = f'ab' if isinstance(data, bytes) else 'a'
  try:
    ensure_path(path)
    with open(path, mode) as f:
      f.write(data)
      return Right(None)
  except OSError as e:
    return Left(e)

def write(path: str | Path, data: str | bytes, *, replace: bool = True) -> Either[FileExistsError | OSError, None]:
  """Write `data` to file at `path`. Returns `Left[FileExistsError]` if `replace is False` and the file exists"""
  access = 'w' if replace else 'x'
  mode = f'{access}b' if isinstance(data, bytes) else access
  try:
    ensure_path(path)
    with open(path, mode) as f:
      f.write(data)
      return Right(None)
  except (FileExistsError, OSError) as e:
    return Left(e)

def update(path: str | Path, data: str | bytes) -> Either[FileNotFoundError | OSError, None]:
  """Write `data` to file at `path`, but only it existed."""
  mode = 'r+b' if isinstance(data, bytes) else 'r+'
  try:
    with open(path, mode) as f:
      f.write(data)
      return Right(None)
  except (FileNotFoundError, OSError) as e:
    return Left(e)
  
def read(path: str) -> Either[FileNotFoundError | OSError, bytes]:
  """Just like `open(path).read()`, with `Either` instead of `raise`"""
  try:
    with open(path, 'rb') as f:
      return Right(f.read())
  except (FileNotFoundError, OSError) as e:
    return Left(e)
      
def delete(path: str, delete_empty: bool = True) -> Either[FileNotFoundError | OSError, None]:
  """Delete file at `path`, plus all parent directories that are left empty if `delete_empty is True` (the default)"""
  try:
    os.remove(path)
    if delete_empty:
      E.safe(lambda: os.removedirs(os.path.dirname(path)))
    return Right(None)
  except (FileNotFoundError, OSError) as e:
    return Left(e)