from sqlalchemy import and_, or_, not_
from sqlalchemy.sql.elements import ClauseElement
from .base_resolver import BaseResolver
from .field_resolver import FieldConditionResolver
from ..models.base_filters import BaseFilter, CombinedFilter, NotFilter, RawFilter
from ..models.entry_filters import BaseEntryFilter
from ..models.field_filters import FieldFilter


class ConditionResolver(BaseResolver):
    """Main resolver that orchestrates all filter resolution"""
    
    def __init__(self, metadata_provider):
        self.metadata_provider = metadata_provider
        self.field_resolver = FieldConditionResolver()
    
    def resolve(self, filter_obj: BaseFilter, context: type | None = None) -> ClauseElement | None:
        """Resolve any filter to SQL condition"""
        if filter_obj is None:
            return None
            
        if isinstance(filter_obj, dict):
            return self._resolve_dict_filter(filter_obj, context)
        elif isinstance(filter_obj, BaseEntryFilter):
            return self._resolve_entry_filter(filter_obj)
        elif isinstance(filter_obj, CombinedFilter):
            return self._resolve_combined_filter(filter_obj, context)
        elif isinstance(filter_obj, NotFilter):
            return self._resolve_not_filter(filter_obj, context)
        elif isinstance(filter_obj, RawFilter):
            return self._resolve_raw_filter(filter_obj)
        else:
            raise ValueError(f"Unsupported filter type: {type(filter_obj)}")
    
    def _resolve_dict_filter(self, filter_dict: dict, model_class: type) -> ClauseElement | None:
        """Resolve dictionary filter (simple key-value pairs)"""
        if not filter_dict or not model_class:
            return None
            
        conditions = []
        for field_name, value in filter_dict.items():
            if hasattr(model_class, field_name):
                column = getattr(model_class, field_name)
                conditions.append(column == value)
        
        return and_(*conditions) if len(conditions) > 1 else (conditions[0] if conditions else None)
    
    def _resolve_entry_filter(self, filter_obj: BaseEntryFilter) -> ClauseElement | None:
        """Resolve entry-specific filter"""
        entry_code = filter_obj.get_entry_code()
        container = self.metadata_provider.get_container_or_raise(entry_code)
        conditions = []
        
        # Process field filters
        for field_name, field_metadata in container.get_all_fields().items():
            field_filter = getattr(filter_obj, field_name, None)
            if field_filter is None:
                continue
                
            if isinstance(field_filter, FieldFilter):
                # Handle regular field filters using metadata
                column = field_metadata.get_column(alias=None)
                condition = self.field_resolver.resolve(field_filter, column)
                if condition is not None:
                    conditions.append(condition)
            
            elif isinstance(field_filter, BaseEntryFilter):
                # Handle nested entry filters using join handlers
                join_handler = container.get_join(field_name)
                if join_handler is not None:
                    # Use alias from join handler for nested filter resolution
                    nested_condition = self._resolve_entry_filter_with_alias(field_filter, join_handler.alias)
                    if nested_condition is not None:
                        conditions.append(nested_condition)
                else:
                    # Fallback: try to resolve without alias
                    nested_condition = self._resolve_entry_filter(field_filter)
                    if nested_condition is not None:
                        conditions.append(nested_condition)
        
        # Process logical operators
        if filter_obj.and_:
            for sub_filter in filter_obj.and_:
                condition = self._resolve_entry_filter(sub_filter)
                if condition is not None:
                    conditions.append(condition)
        
        if filter_obj.or_:
            or_conditions = []
            for sub_filter in filter_obj.or_:
                condition = self._resolve_entry_filter(sub_filter)
                if condition is not None:
                    or_conditions.append(condition)
            if or_conditions:
                conditions.append(or_(*or_conditions))
        
        return and_(*conditions) if len(conditions) > 1 else (conditions[0] if conditions else None)
    
    def _resolve_entry_filter_with_alias(self, filter_obj: BaseEntryFilter, alias) -> ClauseElement | None:
        """Resolve entry-specific filter with provided alias for join"""
        entry_code = filter_obj.get_entry_code()
        container = self.metadata_provider.get_container_or_raise(entry_code)
        conditions = []
        
        # Process field filters with alias
        for field_name, field_metadata in container.get_all_fields().items():
            field_filter = getattr(filter_obj, field_name, None)
            if field_filter is None:
                continue
                
            if isinstance(field_filter, FieldFilter):
                # Handle regular field filters using metadata with alias
                column = field_metadata.get_column(alias=alias)
                condition = self.field_resolver.resolve(field_filter, column)
                if condition is not None:
                    conditions.append(condition)
            
            elif isinstance(field_filter, BaseEntryFilter):
                # Handle nested entry filters using join handlers
                join_handler = container.get_join(field_name)
                if join_handler is not None:
                    # Use alias from join handler for nested filter resolution
                    nested_condition = self._resolve_entry_filter_with_alias(field_filter, join_handler.alias)
                    if nested_condition is not None:
                        conditions.append(nested_condition)
                else:
                    # Fallback: try to resolve without alias
                    nested_condition = self._resolve_entry_filter(field_filter)
                    if nested_condition is not None:
                        conditions.append(nested_condition)
        
        # Process logical operators
        if filter_obj.and_:
            for sub_filter in filter_obj.and_:
                condition = self._resolve_entry_filter_with_alias(sub_filter, alias)
                if condition is not None:
                    conditions.append(condition)
        
        if filter_obj.or_:
            or_conditions = []
            for sub_filter in filter_obj.or_:
                condition = self._resolve_entry_filter_with_alias(sub_filter, alias)
                if condition is not None:
                    or_conditions.append(condition)
            if or_conditions:
                conditions.append(or_(*or_conditions))
        
        return and_(*conditions) if len(conditions) > 1 else (conditions[0] if conditions else None)
    
    def _resolve_combined_filter(self, filter_obj: CombinedFilter, context: type | None = None) -> ClauseElement | None:
        """Resolve combined filter (AND/OR)"""
        conditions = []
        
        for sub_filter in filter_obj.filters:
            condition = self.resolve(sub_filter, context)
            if condition is not None:
                conditions.append(condition)
        
        if not conditions:
            return None
        elif len(conditions) == 1:
            return conditions[0]
        else:
            if filter_obj.operator == "and":
                return and_(*conditions)
            else:  # or
                return or_(*conditions)
    
    def _resolve_not_filter(self, filter_obj: NotFilter, context: type | None = None) -> ClauseElement | None:
        """Resolve NOT filter"""
        condition = self.resolve(filter_obj.filter, context)
        return not_(condition) if condition is not None else None
    
    def _resolve_raw_filter(self, filter_obj: RawFilter) -> ClauseElement | None:
        """Resolve raw SQL filter"""
        return filter_obj.statement 