from typing import TextIO, Iterable, Sequence, Callable
import multiprocessing
import os
from haskellian import iter as I

def chunked_read(file: TextIO, chunk_size: int = 10000) -> Iterable[Sequence[str]]:
  while True:
    lines = file.readlines(chunk_size)
    if not lines:
      break
    yield lines

def parallel_map(
  input: TextIO, output: TextIO,
  func: Callable[[str], str],
  *, chunk_size: int = 10000, num_procs: int | None = None,
  logstream: TextIO | None = None,
):
  count = 0
  num_procs = num_procs or os.cpu_count() or 1
  pool = multiprocessing.Pool(processes=num_procs)
  for chunk in chunked_read(input, chunk_size):
    results = pool.map(func, chunk)
    for result in results:
      output.writelines(result)

    count += len(chunk)
    if logstream:
      print(f'\r{count} lines', end='', flush=True, file=logstream)
