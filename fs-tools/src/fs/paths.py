from typing_extensions import Iterable
import os
from pathlib import Path
from haskellian import iter as I

def ensure_path(file: str | Path):
  """Creates the path to `file`'s folder if it didn't exist
  - E.g. `ensure('path/to/file.txt')` will create `'path/to'` if needed
  """
  dir = os.path.dirname(file)
  if dir != '':
    os.makedirs(dir, exist_ok=True)

@I.lift
def filenames(base_path: str | Path) -> Iterable[str]:
  """Returns all files inside `base_path`, recursively, relative to `base_path`"""
  for root, _, files in os.walk(base_path):
    for file in files:
      path = os.path.join(root, file)
      yield os.path.relpath(path, start=base_path)