# from typing_extensions import TypeVar, Generic
# import asyncio
# from haskellian import ManagedPromise
# from ..api import Queue

# T = TypeVar('T')
# Q = TypeVar('Q', bound=Queue)

# class Bounded(Queue[T], Generic[T]):
  
#   def __init__(self, queue: Queue[T], max_items: int):
#     self._queue = queue
#     self.num_items = 0
#     self.max_items = max_items
#     self._buffer = asyncio.Queue[tuple[str, T]]()
#     self._promise = ManagedPromise()

#   async def _advance(self):
#     k, v = await self._buffer.get()
#     await self._queue.push(k, v)

#   async def push(self, key: str, value: T):
#     await self._buffer.put((key, value))
#     while self.num_items >= self.max_items:
#       if self._promise.resolved:
#         self._promise = ManagedPromise()
#       await self._promise
#     self.num_items += 1
#     await self._advance()
  
#   def _read(self, id: str | None, remove: bool):
#     if remove:
#       self.num_items -= 1
#       self._promise.resolve()
#     return self._queue._read(id, remove)

#   def _items(self):
#     return self._items()
  
# def bounded(queue: Queue[T], max_items: int) -> Queue[T]:
#   return Bounded(queue, max_items)