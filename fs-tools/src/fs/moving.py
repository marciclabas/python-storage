import shutil
from pathlib import Path
from haskellian import Either, Left, Right
from .paths import ensure_path

def copy(src: str | Path, dst: str | Path) -> Either[FileNotFoundError|shutil.SameFileError|OSError, None]:
  """Copy file at `src` to `dst`, creating parent directiories of `dst` if needed"""
  try:
    ensure_path(dst)
    shutil.copy(src, dst)
    return Right(None)
  except (shutil.SameFileError, FileNotFoundError, OSError) as e:
    return Left(e)
  
def move(src: str | Path, dst: str | Path) -> Either[FileNotFoundError|OSError, None]:
  """Copy file at `src` to `dst`, creating parent directiories of `dst` if needed"""
  try:
    ensure_path(dst)
    shutil.move(src, dst)
    return Right(None)
  except (FileNotFoundError, OSError) as e:
    return Left(e)