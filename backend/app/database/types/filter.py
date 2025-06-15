from sqlalchemy import Column
from pydantic import BaseModel
from typing import Any, TypeVar
from enum import Enum
from ...filters.models import BaseFilter

T = TypeVar("T")

class FilterProperty(BaseFilter, BaseModel):
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

    def apply(self, alias):
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
