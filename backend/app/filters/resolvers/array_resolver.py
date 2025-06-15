from sqlalchemy import Column, and_, or_, exists, func
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm import RelationshipProperty, Session
from .base_resolver import BaseResolver
from .field_resolver import FieldConditionResolver
from ..models.field_filters import ArrayFieldFilter, FieldFilter
from ..models.entry_filters import BaseEntryFilter


class ArrayFieldResolver(BaseResolver):
    """Resolver for array field filters with join support"""
    
    def __init__(self, session: Session):
        self.session = session
        self.field_resolver = FieldConditionResolver(session)
    
    def resolve(self, filter_obj: ArrayFieldFilter, context: Column | RelationshipProperty) -> ClauseElement | None:
        """Resolve array field filter to SQL condition with join support"""
        conditions = []
        
        # Handle relationship-based filters (joins)
        if hasattr(context, 'mapper'):
            # This is a relationship, handle as join
            relationship = context
            target_model = relationship.mapper.class_
            
            # Handle any_, all_, none_ filters
            if filter_obj.any_ is not None:
                conditions.append(self._resolve_any_filter(filter_obj.any_, relationship, target_model))
            if filter_obj.all_ is not None:
                conditions.append(self._resolve_all_filter(filter_obj.all_, relationship, target_model))
            if filter_obj.none_ is not None:
                conditions.append(self._resolve_none_filter(filter_obj.none_, relationship, target_model))
                
        # Handle array column filters (for JSON arrays, PostgreSQL arrays, etc.)
        elif isinstance(context, Column):
            # Handle basic array operations
            if filter_obj.is_empty is not None:
                if filter_obj.is_empty:
                    conditions.append(func.array_length(context, 1).is_(None))
                else:
                    conditions.append(func.array_length(context, 1).is_not(None))
            
            if filter_obj.is_not_empty is not None:
                if filter_obj.is_not_empty:
                    conditions.append(func.array_length(context, 1) > 0)
                else:
                    conditions.append(func.array_length(context, 1) == 0)
                    
            if filter_obj.size_eq is not None:
                conditions.append(func.array_length(context, 1) == filter_obj.size_eq)
            if filter_obj.size_gt is not None:
                conditions.append(func.array_length(context, 1) > filter_obj.size_gt)
            if filter_obj.size_lt is not None:
                conditions.append(func.array_length(context, 1) < filter_obj.size_lt)
            if filter_obj.size_gte is not None:
                conditions.append(func.array_length(context, 1) >= filter_obj.size_gte)
            if filter_obj.size_lte is not None:
                conditions.append(func.array_length(context, 1) <= filter_obj.size_lte)
        
        # Handle null checks
        if filter_obj.is_null is not None:
            if filter_obj.is_null:
                conditions.append(context.is_(None))
            else:
                conditions.append(context.is_not(None))
        
        return self._combine_conditions(conditions)
    
    def _resolve_any_filter(self, entry_filter: BaseEntryFilter, relationship: RelationshipProperty, target_model) -> ClauseElement:
        """Resolve 'any' filter - at least one related record matches"""
        subquery_conditions = self._build_entry_conditions(entry_filter, target_model)
        
        # Create EXISTS query
        if subquery_conditions is not None:
            subquery = self.session.query(target_model).filter(subquery_conditions)
            return exists(subquery)
        else:
            # If no conditions, return a condition that's always true
            return True
    
    def _resolve_all_filter(self, entry_filter: BaseEntryFilter, relationship: RelationshipProperty, target_model) -> ClauseElement:
        """Resolve 'all' filter - all related records match (or no records exist)"""
        subquery_conditions = self._build_entry_conditions(entry_filter, target_model)
        
        # Create NOT EXISTS query for records that don't match
        if subquery_conditions is not None:
            inverted_conditions = ~subquery_conditions
            subquery = self.session.query(target_model).filter(inverted_conditions)
            return ~exists(subquery)
        else:
            # If no conditions, all records match by default
            return True
    
    def _resolve_none_filter(self, entry_filter: BaseEntryFilter, relationship: RelationshipProperty, target_model) -> ClauseElement:
        """Resolve 'none' filter - no related records match"""
        subquery_conditions = self._build_entry_conditions(entry_filter, target_model)
        
        # Create NOT EXISTS query
        if subquery_conditions is not None:
            subquery = self.session.query(target_model).filter(subquery_conditions)
            return ~exists(subquery)
        else:
            # If no conditions, return a condition that's always false
            return False
    
    def _build_entry_conditions(self, entry_filter: BaseEntryFilter, target_model) -> ClauseElement | None:
        """Build SQL conditions from BaseEntryFilter"""
        field_conditions = []
        
        # Process all fields in the entry filter
        for field_name, field_value in entry_filter.model_dump(exclude_unset=True, exclude={'and_', 'or_'}).items():
            if field_value is not None and hasattr(target_model, field_name):
                column = getattr(target_model, field_name)
                
                # If it's a FieldFilter, resolve it
                if isinstance(field_value, FieldFilter):
                    condition = self.field_resolver.resolve(field_value, column)
                    if condition is not None:
                        field_conditions.append(condition)
        
        # Handle logical operators (and_, or_)
        if entry_filter.and_:
            for and_filter in entry_filter.and_:
                condition = self._build_entry_conditions(and_filter, target_model)
                if condition is not None:
                    field_conditions.append(condition)
        
        if entry_filter.or_:
            or_conditions = []
            for or_filter in entry_filter.or_:
                condition = self._build_entry_conditions(or_filter, target_model)
                if condition is not None:
                    or_conditions.append(condition)
            if or_conditions:
                field_conditions.append(or_(*or_conditions))
        
        if not field_conditions:
            return None
        
        # Combine all conditions with AND
        return and_(*field_conditions) if len(field_conditions) > 1 else field_conditions[0]
    
    def _combine_conditions(self, conditions: list[ClauseElement]) -> ClauseElement | None:
        """Combine multiple conditions with AND"""
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return and_(*conditions)
        else:
            return None
