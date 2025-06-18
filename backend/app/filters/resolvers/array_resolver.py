from sqlalchemy import Column, and_, or_, func
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm import RelationshipProperty
from .base_resolver import BaseResolver
from ..models.field_filters import ArrayFieldFilter, FieldFilter
from ..models.entry_filters import BaseEntryFilter


class ArrayFieldResolver(BaseResolver):
    """Resolver for array field filters - creates conditions for prepared queries"""
    
    def __init__(self):
        self.field_resolver = None
    
    def resolve(self, filter_obj: ArrayFieldFilter, target_model_class: type) -> dict:
        """
        Resolve array field filter to structured conditions.
        The JOIN handling is done by metadata container.
        """
        result = {
            'type': 'array_filter',
            'target_model': target_model_class,
            'conditions': {}
        }
        
        # Process any_, all_, none_ filters into structured conditions
        if filter_obj.any_ is not None:
            result['conditions']['any'] = self._process_entry_filter(filter_obj.any_, target_model_class)
        if filter_obj.all_ is not None:
            result['conditions']['all'] = self._process_entry_filter(filter_obj.all_, target_model_class)
        if filter_obj.none_ is not None:
            result['conditions']['none'] = self._process_entry_filter(filter_obj.none_, target_model_class)
        
        # Handle basic array operations for direct array columns
        if filter_obj.is_empty is not None:
            result['conditions']['is_empty'] = filter_obj.is_empty
        if filter_obj.is_not_empty is not None:
            result['conditions']['is_not_empty'] = filter_obj.is_not_empty
        if filter_obj.size_eq is not None:
            result['conditions']['size_eq'] = filter_obj.size_eq
        if filter_obj.size_gt is not None:
            result['conditions']['size_gt'] = filter_obj.size_gt
        if filter_obj.size_lt is not None:
            result['conditions']['size_lt'] = filter_obj.size_lt
        if filter_obj.size_gte is not None:
            result['conditions']['size_gte'] = filter_obj.size_gte
        if filter_obj.size_lte is not None:
            result['conditions']['size_lte'] = filter_obj.size_lte
        
        # Handle null checks
        if filter_obj.is_null is not None:
            result['conditions']['is_null'] = filter_obj.is_null
        
        return result
    
    def _process_entry_filter(self, entry_filter: BaseEntryFilter, target_model_class: type) -> dict:
        """Process BaseEntryFilter into structured conditions"""
        field_conditions = {}
        
        # Process all fields in the entry filter
        for field_name, field_value in entry_filter.model_dump(exclude_unset=True, exclude={'and_', 'or_'}).items():
            if field_value is not None and hasattr(target_model_class, field_name):
                column = getattr(target_model_class, field_name)
                
                # If it's a FieldFilter, resolve it
                if isinstance(field_value, FieldFilter):
                    # Lazy initialization to avoid circular imports
                    if self.field_resolver is None:
                        from .field_resolver import FieldConditionResolver
                        self.field_resolver = FieldConditionResolver()
                    
                    condition = self.field_resolver.resolve(field_value, column)
                    if condition is not None:
                        field_conditions[field_name] = condition
        
        result = {
            'field_conditions': field_conditions,
            'logical_operators': {}
        }
        
        # Handle logical operators (and_, or_)
        if entry_filter.and_:
            and_conditions = []
            for and_filter in entry_filter.and_:
                and_conditions.append(self._process_entry_filter(and_filter, target_model_class))
            result['logical_operators']['and'] = and_conditions
        
        if entry_filter.or_:
            or_conditions = []
            for or_filter in entry_filter.or_:
                or_conditions.append(self._process_entry_filter(or_filter, target_model_class))
            result['logical_operators']['or'] = or_conditions
        
        return result
