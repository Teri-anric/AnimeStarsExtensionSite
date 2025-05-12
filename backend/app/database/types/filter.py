from abc import ABC, abstractmethod
from sqlalchemy import Column, and_, or_, not_, text
from pydantic import BaseModel
from typing import Any, TypeVar
from enum import Enum


T = TypeVar("T")


class Filter(ABC, BaseModel):
    @abstractmethod
    def apply(self, alias: T):
        pass

    def __and__(self, other: "Filter"):
        return AndFilter(filters=[self, other])

    def __or__(self, other: "Filter"):
        return OrFilter(filters=[self, other])

    def __invert__(self):
        return NotFilter(filter=self)


class FilterProperty(Filter, BaseModel):
    class Operator(str, Enum):
        EQ = "eq"
        NE = "ne"
        GT = "gt"
        LT = "lt"
        GTE = "gte"
        LTE = "lte"
        IN = "in"
        NOT_IN = "not_in"
        LIKE = "like"
        NOT_LIKE = "not_like"
        IS = "is"
        IS_NOT = "is_not"

    property: str
    operator: Operator = Operator.EQ
    value: Any = None

    def apply(self, alias: T):
        column: Column = getattr(alias, self.property)
        operator_method = {
            self.Operator.EQ: column.__eq__,
            self.Operator.NE: column.__ne__,
            self.Operator.GT: column.__gt__,
            self.Operator.LT: column.__lt__,
            self.Operator.GTE: column.__ge__,
            self.Operator.LTE: column.__le__,
            self.Operator.IN: column.in_,
            self.Operator.NOT_IN: column.not_in,
            self.Operator.LIKE: column.like,
            self.Operator.NOT_LIKE: column.not_like,
            self.Operator.IS: column.is_,
            self.Operator.IS_NOT: column.is_not,
        }
        return operator_method[self.operator](self.value)


class AndFilter(Filter, BaseModel):
    filters: list[Filter]

    def apply(self, alias: T):
        return and_(*[filter.apply(alias) for filter in self.filters])

class OrFilter(Filter, BaseModel):
    filters: list[Filter]

    def apply(self, alias: T):
        return or_(*[filter.apply(alias) for filter in self.filters])

class NotFilter(Filter, BaseModel):
    filter: Filter

    def apply(self, alias: T):
        return not_(self.filter.apply(alias))

class RawFilter(Filter, BaseModel):
    statement: Any

    def apply(self, alias: T):
        return self.statement
