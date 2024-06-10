from typing import Sequence

import tarfile
import io

def create_tarfile(files: Sequence[tuple[str, bytes]], filename: str = 'files.tar'):
  """Create a tarfile `filename` containing the files in `files`
  - `files[i][0]`: filename
  - `files[i][1]`: file content
  """
  with tarfile.open(filename, 'w') as tar:
    for name, file in files:
      file_info = tarfile.TarInfo(name=name)
      file_info.size = len(file)
      tar.addfile(file_info, fileobj=io.BytesIO(file))