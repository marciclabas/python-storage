# from typing_extensions import TypeVar, Generic, AsyncIterable
# import asyncio
# from haskellian import ManagedAsync
# from ..api import ReadQueue
# from ..impl import SimpleQueue

# A = TypeVar('A')
# B = TypeVar('B')
# C = TypeVar('C')

# class Interleaved(ReadQueue[A], Generic[A]):

#   def __init__(self, queues: list[ReadQueue[A]]):
#     self._queues = queues
#     self._buffer: SimpleQueue[A] = SimpleQueue()

#   async def _advance(self):
#     for fut in asyncio.as_completed([q.pop() for q in self._queues]):
#       k, v = await fut
#       await self._buffer.push(k, v)

#   async def _read(self, id: str | None = None, remove: bool = False) -> tuple[str, A] | A | None:
#     if id is None:
#       if len(self._buffer) == 0:
#         asyncio.create_task(self._advance())
#       return await self._buffer._read(id, remove)
#     else:
#       for q in self._queues:
#         x = await q._read(id, remove)
#         if x is not None:
#           return x
  
#   def _items(self) -> AsyncIterable[tuple[str, A]]:
#     out = ManagedAsync[tuple[str, A]]()
#     async def iterate(xs: AsyncIterable[tuple[str, A]]):
#       async for x in xs:
#         out.push(x)

#     async def iterate_all():
#       async for x in self._buffer.items():
#         out.push(x)
#       await asyncio.gather(*[iterate(q.items()) for q in self._queues])
#       out.end()
#     asyncio.create_task(iterate_all())
#     return out
  
# def interleave(q1: ReadQueue[A], q2: ReadQueue[B], *qs: ReadQueue[C]) -> ReadQueue[A|B|C]:
#   return Interleaved[A|B|C]([q1, q2, *qs])