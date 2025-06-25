from sqlalchemy import Column, and_
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm import RelationshipProperty, Session
from .base_resolver import BaseResolver
from datetime import datetime, timedelta
from ..models.field_filters import (
    FieldFilter,
    StringFieldFilter,
    NumericFieldFilter,
    DateTimeFieldFilter,
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
        elif isinstance(filter_obj, DateTimeFieldFilter):
            return self._resolve_datetime_filter(filter_obj, context)
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

    def _resolve_datetime_filter(self, filter_obj: DateTimeFieldFilter, column: Column) -> ClauseElement | None:
        """Resolve datetime field filter with user-friendly operators"""
        conditions = []
        now = datetime.now()
        
        # Exact datetime comparisons
        if filter_obj.eq is not None:
            conditions.append(column == filter_obj.eq)
        if filter_obj.ne is not None:
            conditions.append(column != filter_obj.ne)
        if filter_obj.before is not None:
            conditions.append(column < filter_obj.before)
        if filter_obj.after is not None:
            conditions.append(column > filter_obj.after)
        if filter_obj.between is not None:
            start_date, end_date = filter_obj.between
            conditions.append(and_(column >= start_date, column <= end_date))
        
        # Relative date filters
        if filter_obj.today is True:
            start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_today = start_of_today + timedelta(days=1)
            conditions.append(and_(column >= start_of_today, column < end_of_today))
        
        if filter_obj.yesterday is True:
            start_of_yesterday = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end_of_yesterday = start_of_yesterday + timedelta(days=1)
            conditions.append(and_(column >= start_of_yesterday, column < end_of_yesterday))
        
        if filter_obj.this_week is True:
            days_since_monday = now.weekday()
            start_of_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            end_of_week = start_of_week + timedelta(days=7)
            conditions.append(and_(column >= start_of_week, column < end_of_week))
        
        if filter_obj.last_week is True:
            days_since_monday = now.weekday()
            start_of_last_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday + 7)
            end_of_last_week = start_of_last_week + timedelta(days=7)
            conditions.append(and_(column >= start_of_last_week, column < end_of_last_week))
        
        if filter_obj.this_month is True:
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Get next month
            if now.month == 12:
                end_of_month = start_of_month.replace(year=now.year + 1, month=1)
            else:
                end_of_month = start_of_month.replace(month=now.month + 1)
            conditions.append(and_(column >= start_of_month, column < end_of_month))
        
        if filter_obj.last_month is True:
            # Get start of last month
            if now.month == 1:
                start_of_last_month = now.replace(year=now.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_of_last_month = now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get start of this month (end of last month)
            start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            conditions.append(and_(column >= start_of_last_month, column < start_of_this_month))
        
        if filter_obj.this_year is True:
            start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_year = start_of_year.replace(year=now.year + 1)
            conditions.append(and_(column >= start_of_year, column < end_of_year))
        
        if filter_obj.last_year is True:
            start_of_last_year = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_last_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            conditions.append(and_(column >= start_of_last_year, column < end_of_last_year))
        
        # Days-based filters
        if filter_obj.last_n_days is not None:
            n_days_ago = now - timedelta(days=filter_obj.last_n_days)
            conditions.append(column >= n_days_ago)
        
        if filter_obj.older_than_days is not None:
            threshold_date = now - timedelta(days=filter_obj.older_than_days)
            conditions.append(column < threshold_date)
        
        # Null checks
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