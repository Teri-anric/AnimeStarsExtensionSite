from typing import Any
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy import Select, and_, or_
from .parser.filter_parser import FilterParser
from .resolvers.condition_resolver import ConditionResolver
from .metadata import MetadataProvider
from .models.base_filters import BaseFilter
from .models.entry_filters import BaseEntryFilter


class FilterService:
    """Service that orchestrates filter parsing and resolution"""
    
    def __init__(self, metadata_provider: MetadataProvider):
        self.metadata_provider = metadata_provider
        self.parser = FilterParser(metadata_provider)
        self.resolver = ConditionResolver(metadata_provider)
    
    def register_entry_filter(self, filter_class) -> "FilterService":
        """Register an entry filter class"""
        self.parser.register_entry_filter(filter_class)
        return self
    
    def parse_and_resolve(
        self, 
        filter_data: Any, 
        entry_code: str | None = None,
        model_class: type | None = None
    ) -> ClauseElement | None:
        """Parse filter data and resolve to SQL condition"""
        # Parse the filter data
        parsed_filter = self.parser.parse(filter_data, entry_code)
        if parsed_filter is None:
            return None
        
        # Resolve to SQL condition
        return self.resolver.resolve(parsed_filter, model_class)
    
    def parse(self, filter_data: Any, entry_code: str | None = None) -> BaseFilter | None:
        """Parse filter data into filter models"""
        return self.parser.parse(filter_data, entry_code)
    
    def resolve(self, filter_obj: BaseFilter, model_class: type | None = None) -> ClauseElement | None:
        """Resolve filter to SQL condition"""
        return self.resolver.resolve(filter_obj, model_class)
    
    def prepare_query_with_metadata(self, stmt: Select, filter_data: Any) -> Select:
        """
        Prepare query by adding necessary JOINs based on entry filters.
        Repository passes stmt and filter_data.
        """
        if not filter_data:
            return stmt
        
        # Parse filter - parser will auto-detect entry filter type
        parsed_filter = self.parser.parse(filter_data)
        if not parsed_filter or not isinstance(parsed_filter, BaseEntryFilter):
            return stmt
        
        # Get entry code from parsed filter
        entry_code = parsed_filter.get_entry_code()
        
        # Process joins for entry filters
        stmt = self._prepare_joins_for_entry_filter(stmt, parsed_filter, entry_code)
        
        return stmt
    
    def _prepare_joins_for_entry_filter(self, stmt: Select, entry_filter: BaseEntryFilter, entry_code: str) -> Select:
        """Recursively prepare joins for entry filter and its nested entry filters"""
        if not self.metadata_provider.has_container(entry_code):
            return stmt
            
        container = self.metadata_provider.get_container(entry_code)
        
        # Check for entry filters that need joins
        for field_name in entry_filter.model_dump(exclude_unset=True).keys():
            field_value = getattr(entry_filter, field_name, None)
            if field_value is not None and hasattr(field_value, 'get_entry_code'):
                # This is an entry filter - check if we have a join handler
                join_handler = container.get_join(field_name)
                if join_handler is not None:
                    stmt = join_handler.prepare_query(stmt)
                    
                    # Recursively process nested entry filter
                    nested_entry_code = field_value.get_entry_code()
                    stmt = self._prepare_joins_for_entry_filter(stmt, field_value, nested_entry_code)
        
        # Handle logical operators
        if hasattr(entry_filter, 'and_') and entry_filter.and_:
            for sub_filter in entry_filter.and_:
                stmt = self._prepare_joins_for_entry_filter(stmt, sub_filter, entry_code)
        
        if hasattr(entry_filter, 'or_') and entry_filter.or_:
            for sub_filter in entry_filter.or_:
                stmt = self._prepare_joins_for_entry_filter(stmt, sub_filter, entry_code)
        
        return stmt 
    
 