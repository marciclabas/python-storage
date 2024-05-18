# from typing_extensions import TypeVar, Generic, AsyncIterable, Callable, Awaitable
# from haskellian import promise as P, Either, Left, Right
# from .. import ReadQueue, WriteQueue, QueueError, InexistentItem
# from ..impl import SimpleQueue
# from .interleaving import interleave

# A = TypeVar('A', covariant=True)
# B = TypeVar('B')
# C = TypeVar('C')

# class Split(ReadQueue[A], Generic[A]):

#   def __init__(self, split: Callable[[C], tuple[A, B] | Awaitable[tuple[A, B]]], queue: ReadQueue[C], other: WriteQueue[B]):
#     self._split = split
#     self._queue = queue
#     self._other = other

#   async def _read(self, id: str | None, remove: bool) -> Either[QueueError | InexistentItem, tuple[str, A]]:
#     match await self._queue._read(id, remove):
#       case Right((id, v)):
#         a, b = await P.wait(self._split(v))
#         await self._other.push(id, b)
#         return Right((id, a))
#       case err:
#         return err # type: ignore
  
#   async def _items(self) -> AsyncIterable[Either[QueueError, tuple[str, A]]]:
#     async for e in self._queue._items():
#       match e:
#         case Right((id, v)):
#           a, _ = await P.wait(self._split(v))
#           yield Right((id, a))
#         case err:
#           yield err # type: ignore

# def swap(pair: tuple[A, B]) -> tuple[B, A]:
#   a, b = pair
#   return b, a

# def split(
#   queue: ReadQueue[A],
#   split: Callable[[A], tuple[B, C] | Awaitable[tuple[B, C]]]
# ) -> tuple[ReadQueue[B], ReadQueue[C]]:
#   buf1 = SimpleQueue[B]()
#   buf2 = SimpleQueue[C]()
#   q1 = interleave(buf1, Split(split, queue, buf2))
#   q2 = interleave(buf2, Split(lambda x: P.wait(split(x)).then(swap), queue, buf1))
#   q1.__name__ = f'Split{repr(queue)}1'
#   q2.__name__ = f'Split{repr(queue)}2'
#   return q1, q2

# def unzip(queue: ReadQueue[tuple[A, B]]) -> tuple[ReadQueue[A], ReadQueue[B]]:
#   q1, q2 = split(queue, lambda x: x)
#   q1.__name__ = f'Unzipped{repr(queue)}1'
#   q2.__name__ = f'Unzipped{repr(queue)}2'
#   return q1, q2

# def extend(
#   queue: ReadQueue[A],
#   extend: Callable[[A], B | Awaitable[B]]
# ) -> tuple[ReadQueue[A], ReadQueue[B]]:
#   """`q1, q2 = extend(q, f)` is roughly equivalent to `q1 = q; q2 = q.map(f)`, except `q1` and `q2` are independent (popping one doesn't affect the other)"""
#   return split(queue, lambda x: P.wait(extend(x)).then(lambda r: (x, r)))