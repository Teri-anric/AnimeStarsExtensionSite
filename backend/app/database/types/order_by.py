from pydantic import BaseModel
from sqlalchemy import asc, desc
from typing import TypeVar
from enum import Enum


T = TypeVar("T")


class OrderBy(BaseModel):
    class Sort(BaseModel):
        class Direction(str, Enum):
            ASC = "asc"
            DESC = "desc"

        property: str
        direction: Direction = Direction.DESC

    sorts: list[Sort] = []

    def apply(self, alias: T):
        order_by = []
        for sort in self.sorts:
            column = getattr(alias, sort.property)
            if sort.direction == OrderBy.Sort.Direction.ASC:
                order_by.append(asc(column))
                continue
            order_by.append(desc(column))
        return order_by
