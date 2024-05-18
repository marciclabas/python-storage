# Sql Types

> Custom types for SQLModel/SQLalchemy

## Usage

```python
from typing import Sequence
from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqltypes import PydanticModel, SpaceDelimitedList

class User(BaseModel):
  name: str
  age: int

class MyDBItem(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  tags: Sequence[str] = Field(sa_type=SpaceDelimitedList)
  user: User = Field(sa_type=PydanticModel(User))
```