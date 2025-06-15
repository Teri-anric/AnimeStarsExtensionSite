from typing import Any
from sqlalchemy.sql.elements import ClauseElement
from .parser.filter_parser import FilterParser
from .resolvers.condition_resolver import ConditionResolver
from .metadata import MetadataProvider
from .models.base_filters import BaseFilter


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