"""
### Key-Value Api
> API spec for an async Key-Value DB

- Details
"""
from .kv import KV
from .impl import SimpleKV
from .errors import DBError, InexistentItem, InvalidData, ReadError
from .extensions import AppendableKV, SimpleAppendKV, Appendable, Locatable, LocatableKV

__all__ = [
  'KV',
  'SimpleKV',
  'DBError', 'InexistentItem', 'InvalidData', 'ReadError',
  'AppendableKV', 'SimpleAppendKV', 'Appendable', 'Locatable', 'LocatableKV'
]
