from abc import ABC, abstractmethod
from sqlalchemy import Column, and_, or_, not_
from pydantic import BaseModel, Field
from typing import Any, TypeVar,  Type, Generic, Self
from enum import Enum


T = TypeVar("T")


class BaseFilter(ABC, BaseModel):
    """Base class for all filters"""
    
    @abstractmethod
    def apply(self, model_class: Type[T]):
        """Apply filter to SQLAlchemy model class"""
        pass

    def __and__(self, other: "BaseFilter"):
        return CombinedFilter(operator="and", filters=[self, other])

    def __or__(self, other: "BaseFilter"):
        return CombinedFilter(operator="or", filters=[self, other])

    def __invert__(self):
        return NotFilter(filter=self)


class FieldFilter(ABC, BaseModel):
    """Base class for field-specific filters that parse operator-value pairs"""
    
    @abstractmethod
    def apply(self, column: Column):
        """Apply filter to SQLAlchemy column"""
        pass


class EnumFliedFilter(FieldFilter, Generic[T]):
    eq: T | None = None
    ne: T | None = None
    in_: list[T] | None = Field(None, alias="in")
    not_in: list[T] | None = None
    is_null: bool | None = None
    

    def apply(self, column: Column):
        conditions = []
        
        if self.eq is not None:
            conditions.append(column == self.eq)
        if self.ne is not None:
            conditions.append(column != self.ne)
        if self.in_ is not None:
            conditions.append(column.in_(self.in_))
        if self.not_in is not None:
            conditions.append(column.not_in(self.not_in))
        if self.is_null is not None:
            if self.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None

class NumericFieldFilter(FieldFilter):
    """Filter for numeric fields with comparison operators"""
    
    eq: int | float | None = None
    ne: int | float | None = None
    gt: int | float | None = None
    lt: int | float | None = None
    gte: int | float | None = None
    lte: int | float | None = None
    in_: list[int | float] | None = Field(None, alias="in")
    not_in: list[int | float] | None = None
    is_null: bool | None = None
    
    def apply(self, column: Column):
        conditions = []
        
        if self.eq is not None:
            conditions.append(column == self.eq)
        if self.ne is not None:
            conditions.append(column != self.ne)
        if self.gt is not None:
            conditions.append(column > self.gt)
        if self.lt is not None:
            conditions.append(column < self.lt)
        if self.gte is not None:
            conditions.append(column >= self.gte)
        if self.lte is not None:
            conditions.append(column <= self.lte)
        if self.in_ is not None:
            conditions.append(column.in_(self.in_))
        if self.not_in is not None:
            conditions.append(column.not_in(self.not_in))
        if self.is_null is not None:
            if self.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None


class StringFieldFilter(FieldFilter):
    """Filter for string fields with text-specific operators"""
    
    eq: str | None = None
    ne: str | None = None
    like: str | None = None
    ilike: str | None = None  # case-insensitive like
    not_like: str | None = None
    in_: list[str] | None = Field(None, alias="in")
    not_in: list[str] | None = None
    is_null: bool | None = None
    
    def apply(self, column: Column):
        conditions = []
        
        if self.eq is not None:
            conditions.append(column == self.eq)
        if self.ne is not None:
            conditions.append(column != self.ne)
        if self.like is not None:
            conditions.append(column.like(self.like))
        if self.ilike is not None:
            conditions.append(column.ilike(self.ilike))
        if self.not_like is not None:
            conditions.append(column.not_like(self.not_like))
        if self.in_ is not None:
            conditions.append(column.in_(self.in_))
        if self.not_in is not None:
            conditions.append(column.not_in(self.not_in))
        if self.is_null is not None:
            if self.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None


class BooleanFieldFilter(FieldFilter):
    """Filter for boolean fields"""
    
    eq: bool | None = None
    is_null: bool | None = None
    
    def apply(self, column: Column):
        conditions = []
        
        if self.eq is not None:
            conditions.append(column == self.eq)
        if self.is_null is not None:
            if self.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None


class EntryFilter(BaseFilter):
    """Base class for model-specific filters"""
    and_: list[Self] | None = Field(None, alias="and")
    or_: list[Self] | None = Field(None, alias="or")

    def apply(self, model_class: Type[T]):
        """Apply all field filters to the model"""
        conditions = []
        
        for field_name in self.model_fields_set:
            if field_name in ["and_", "or_"]:
                continue
            field_filter = getattr(self, field_name)
            if isinstance(field_filter, FieldFilter):
                column: Column = getattr(model_class, field_name)
                condition = field_filter.apply(column)
                if condition is not None:
                    conditions.append(condition)
        
        if self.and_ is not None:
            conditions.append(and_(*[filter.apply(model_class) for filter in self.and_]))
        if self.or_ is not None:
            conditions.append(or_(*[filter.apply(model_class) for filter in self.or_]))
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None



class CombinedFilter(BaseFilter):
    """Filter that combines multiple filters with AND/OR operators"""
    
    operator: str  # "and" or "or"
    filters: list[BaseFilter]
    
    def apply(self, model_class: Type[T]):
        conditions = []
        
        for filter_item in self.filters:
            condition = filter_item.apply(model_class)
            if condition is not None:
                conditions.append(condition)
        
        if not conditions:
            return None
        elif len(conditions) == 1:
            return conditions[0]
        else:
            if self.operator == "and":
                return and_(*conditions)
            else:  # or
                return or_(*conditions)


class NotFilter(BaseFilter):
    """Filter that negates another filter"""
    
    filter: BaseFilter
    
    def apply(self, model_class: Type[T]):
        condition = self.filter.apply(model_class)
        return not_(condition) if condition is not None else None


class RawFilter(BaseFilter):
    """Filter for raw SQL conditions"""
    
    statement: Any
    
    def apply(self, model_class: Type[T]):
        return self.statement


# Legacy compatibility (deprecated)
class FilterProperty(BaseFilter, BaseModel):
    """Legacy filter property class - use ModelFilter instead"""
    
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

    def apply(self, model_class: Type[T]):
        column: Column = getattr(model_class, self.property)
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
