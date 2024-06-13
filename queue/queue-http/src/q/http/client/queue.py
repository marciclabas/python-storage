from typing import TypeVar, Generic, overload, Callable
from urllib.parse import urljoin
from pydantic import RootModel
from haskellian import Either, Right, either as E
from q.api import Queue, QueueError
from .read import ReadClientQ
from .write import WriteClientQ

T = TypeVar('T')

class ClientQueue(Queue[T], ReadClientQ[T], WriteClientQ[T], Generic[T]):

  @overload
  def __init__(
    self, url: str, *,
    parse: Callable[[bytes], Either[QueueError, T]] = Right,
    dump: Callable[[T], bytes] = lambda x: x # type: ignore
  ): ...
  @overload
  def __init__(
    self, *, read_url: str, write_url: str,
    parse: Callable[[bytes], Either[QueueError, T]] = Right,
    dump: Callable[[T], bytes] = lambda x: x # type: ignore
  ): ...
  def __init__(
    self, url = None, *, read_url = None, write_url = None,
    parse: Callable[[bytes], Either[QueueError, T]] = Right, dump = lambda x: x
  ):
    if url:
      self.read_url = urljoin(url, 'read')
      self.write_url = urljoin(url, 'write')
    elif read_url and write_url:
      self.read_url = read_url
      self.write_url = write_url
    else:
      raise ValueError('Either url or (read_url and write_url) must be provided')

    ReadClientQ.__init__(self, self.read_url, parse=parse)
    WriteClientQ.__init__(self, self.write_url, dump=dump)


  @overload
  @classmethod
  def validated(cls, Type: type[T], url: str) -> 'ClientQueue[T]': ...
  @overload
  @classmethod
  def validated(cls, Type: type[T], *, read_url: str, write_url: str) -> 'ClientQueue[T]': ...
  @classmethod
  def validated(cls, Type, url = None, *, read_url = None, write_url = None) -> 'ClientQueue[T]':
    Model = RootModel[Type]
    return cls(
      url=url, read_url=read_url, write_url=write_url,
      parse=lambda b: E.validate_json(b, Model).fmap(lambda x: x.root).mapl(QueueError),
      dump=lambda x: Model(x).model_dump_json(exclude_none=True)
    ) # type: ignore