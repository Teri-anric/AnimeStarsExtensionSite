from sqlalchemy import Column, and_
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm import RelationshipProperty, Session
from .base_resolver import BaseResolver
from ..models.field_filters import (
    FieldFilter,
    StringFieldFilter,
    NumericFieldFilter,
    BooleanFieldFilter,
    EnumFieldFilter,
    ArrayFieldFilter,
)


class FieldConditionResolver(BaseResolver):
    """Resolver for field-specific filters"""
    
    def __init__(self, session: Session = None):
        self.session = session
        # Import here to avoid circular imports
        if session:
            from .array_resolver import ArrayFieldResolver
            self.array_resolver = ArrayFieldResolver(session)
        else:
            self.array_resolver = None
    
    def resolve(self, filter_obj: FieldFilter, context: Column | RelationshipProperty) -> ClauseElement | None:
        """Resolve field filter to SQL condition"""
        if isinstance(filter_obj, StringFieldFilter):
            return self._resolve_string_filter(filter_obj, context)
        elif isinstance(filter_obj, NumericFieldFilter):
            return self._resolve_numeric_filter(filter_obj, context)
        elif isinstance(filter_obj, BooleanFieldFilter):
            return self._resolve_boolean_filter(filter_obj, context)
        elif isinstance(filter_obj, EnumFieldFilter):
            return self._resolve_enum_filter(filter_obj, context)
        elif isinstance(filter_obj, ArrayFieldFilter):
            if self.array_resolver:
                return self.array_resolver.resolve(filter_obj, context)
            else:
                raise ValueError("ArrayFieldFilter requires a session for join operations")
        else:
            raise ValueError(f"Unsupported field filter type: {type(filter_obj)}")
    
    def _resolve_string_filter(self, filter_obj: StringFieldFilter, column: Column) -> ClauseElement | None:
        """Resolve string field filter"""
        conditions = []
        
        if filter_obj.eq is not None:
            conditions.append(column == filter_obj.eq)
        if filter_obj.ne is not None:
            conditions.append(column != filter_obj.ne)
        if filter_obj.like is not None:
            conditions.append(column.like(filter_obj.like))
        if filter_obj.ilike is not None:
            conditions.append(column.ilike(filter_obj.ilike))
        if filter_obj.not_like is not None:
            conditions.append(column.not_like(filter_obj.not_like))
        if filter_obj.contains is not None:
            conditions.append(column.like(f'%{filter_obj.contains}%'))
        if filter_obj.icontains is not None:
            conditions.append(column.ilike(f'%{filter_obj.icontains}%'))
        if filter_obj.not_contains is not None:
            conditions.append(column.not_like(f'%{filter_obj.not_contains}%'))
        if filter_obj.in_ is not None:
            conditions.append(column.in_(filter_obj.in_))
        if filter_obj.not_in is not None:
            conditions.append(column.not_in(filter_obj.not_in))
        if filter_obj.is_null is not None:
            if filter_obj.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        return self._combine_conditions(conditions)
    
    def _resolve_numeric_filter(self, filter_obj: NumericFieldFilter, column: Column) -> ClauseElement | None:
        """Resolve numeric field filter"""
        conditions = []
        
        if filter_obj.eq is not None:
            conditions.append(column == filter_obj.eq)
        if filter_obj.ne is not None:
            conditions.append(column != filter_obj.ne)
        if filter_obj.gt is not None:
            conditions.append(column > filter_obj.gt)
        if filter_obj.lt is not None:
            conditions.append(column < filter_obj.lt)
        if filter_obj.gte is not None:
            conditions.append(column >= filter_obj.gte)
        if filter_obj.lte is not None:
            conditions.append(column <= filter_obj.lte)
        if filter_obj.in_ is not None:
            conditions.append(column.in_(filter_obj.in_))
        if filter_obj.not_in is not None:
            conditions.append(column.not_in(filter_obj.not_in))
        if filter_obj.is_null is not None:
            if filter_obj.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        return self._combine_conditions(conditions)
    
    def _resolve_boolean_filter(self, filter_obj: BooleanFieldFilter, column: Column) -> ClauseElement | None:
        """Resolve boolean field filter"""
        conditions = []
        
        if filter_obj.eq is not None:
            conditions.append(column == filter_obj.eq)
        if filter_obj.is_null is not None:
            if filter_obj.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        return self._combine_conditions(conditions)
    
    def _resolve_enum_filter(self, filter_obj: EnumFieldFilter, column: Column) -> ClauseElement | None:
        """Resolve enum field filter"""
        conditions = []
        
        if filter_obj.eq is not None:
            conditions.append(column == filter_obj.eq)
        if filter_obj.ne is not None:
            conditions.append(column != filter_obj.ne)
        if filter_obj.in_ is not None:
            conditions.append(column.in_(filter_obj.in_))
        if filter_obj.not_in is not None:
            conditions.append(column.not_in(filter_obj.not_in))
        if filter_obj.is_null is not None:
            if filter_obj.is_null:
                conditions.append(column.is_(None))
            else:
                conditions.append(column.is_not(None))
        
        return self._combine_conditions(conditions)
    
    def _combine_conditions(self, conditions: list[ClauseElement]) -> ClauseElement | None:
        """Combine multiple conditions with AND"""
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None 