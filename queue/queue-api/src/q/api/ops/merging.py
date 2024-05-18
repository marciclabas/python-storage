# from typing_extensions import TypeVar, Generic, AsyncIterable, Callable, Awaitable
# import asyncio
# import haskellian.promise as P
# from q.api import ReadQueue

# A = TypeVar('A')
# B = TypeVar('B')
# C = TypeVar('C')


# class Merged(ReadQueue[C], Generic[A, B, C]):

#   def __init__(self, merge: Callable[[str, tuple[A, B]], C | Awaitable[C]], queues: tuple[ReadQueue[A], ReadQueue[B]]):
#     self._merge = merge
#     self._q1 = queues[0]
#     self._q2 = queues[1]

#   async def _read_one(self, id: str | None = None) -> None | tuple[str, A, B]:
#     if id is not None:
#       x1, x2 = await asyncio.gather(self._q1.read(id), self._q2.read(id))
#       if x1 is not None and x2 is not None:
#         return id, x1, x2
#     else:
#       async for k, x1 in self._q1._items():
#         x2 = await self._q2.read(k)
#         if x2 is not None:
#           return k, x1, x2

#   async def _read(self, id: str | None = None, remove: bool = False) -> None | tuple[str, C]:
#     while True:
#       match await self._read_one(id):
#         case k, x1, x2:
#           if remove:
#             await asyncio.gather(self._q1.pop(k), self._q2.pop(k))
#           return k, await P.wait(self._merge(k, (x1, x2)))
#       for fut in asyncio.as_completed((self._q1.read(), self._q2.read())):
#         await fut

#   async def _items(self) -> AsyncIterable[tuple[str, C]]:
#     async for k, x1 in self._q1._items():
#       x2 = await self._q2.read(k)
#       if x2 is not None:
#         yield k, await P.wait(self._merge(k, (x1, x2)))

# def merge(queues: tuple[ReadQueue[A], ReadQueue[B]], merge: Callable[[str, tuple[A, B]], C | Awaitable[C]]) -> ReadQueue[C]:
#   return Merged(merge, queues)

# def zip(queues: tuple[ReadQueue[A], ReadQueue[B]]) -> ReadQueue[tuple[A, B]]:
#   return merge(queues, lambda k, t: t)