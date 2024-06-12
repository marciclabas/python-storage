from typing import TypeVar, Generic, overload
from urllib.parse import urljoin
from q.api import Queue
from .read import ReadClientQ
from .write import WriteClientQ

T = TypeVar('T')

class ClientQueue(Queue[T], ReadClientQ[T], WriteClientQ[T], Generic[T]):

  @overload
  def __init__(self, Type: type[T], url: str): ...
  @overload
  def __init__(self, Type: type[T], *, read_url: str, write_url: str): ...
  def __init__(self, Type: type[T], url = None, *, read_url = None, write_url = None):
    if url:
      self.read_url = urljoin(url, 'read')
      self.write_url = urljoin(url, 'write')
    elif read_url and write_url:
      self.read_url = read_url
      self.write_url = write_url
    else:
      raise ValueError('Either url or (read_url and write_url) must be provided')

    ReadClientQ.__init__(self, Type, self.read_url)
    WriteClientQ.__init__(self, Type, self.write_url)