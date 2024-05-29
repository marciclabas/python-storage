from typing import Iterable, Sequence

def concat_lines(filepaths: Sequence[str]) -> Iterable[str]:
  for file in filepaths:
    with open(file, 'r') as f:
      for line in f:
        yield line