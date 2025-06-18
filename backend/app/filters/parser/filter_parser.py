from typing import Any, Dict, Type
from ..models.base_filters import BaseFilter, CombinedFilter, NotFilter, RawFilter
from ..models.entry_filters import BaseEntryFilter
from ..metadata import MetadataProvider


class FilterParser:
    """Parser that converts JSON/dict input to filter models"""
    
    def __init__(self, metadata_provider: MetadataProvider):
        self.metadata_provider = metadata_provider
        self._entry_filter_registry: Dict[str, Type[BaseEntryFilter]] = {}
    
    def register_entry_filter(self, filter_class: Type[BaseEntryFilter]) -> "FilterParser":
        """Register an entry filter class"""
        entry_code = filter_class.get_entry_code()
        self._entry_filter_registry[entry_code] = filter_class
        return self
    
    def parse(self, filter_data: Any, entry_code: str | None = None) -> BaseFilter | None:
        """Parse filter data into filter models"""
        if filter_data is None:
            return None
        
        # If it's already a BaseFilter or BaseEntryFilter object, return as is
        if isinstance(filter_data, (BaseFilter, BaseEntryFilter)):
            return filter_data
            
        if isinstance(filter_data, dict):
            return self._parse_dict_filter(filter_data, entry_code)
        else:
            raise ValueError(f"Unsupported filter data type: {type(filter_data)}")
    

    def _parse_dict_filter(self, filter_dict: dict, entry_code: str | None = None) -> BaseFilter | None:
        """Parse dictionary filter"""
        if not filter_dict:
            return None
        
        # Check for logical operators
        if "and" in filter_dict or "or" in filter_dict:
            return self._parse_combined_filter(filter_dict, entry_code)
        
        if "not" in filter_dict:
            return self._parse_not_filter(filter_dict, entry_code)
        
        # If entry_code provided, use it
        if entry_code and entry_code in self._entry_filter_registry:
            return self._parse_entry_filter(filter_dict, entry_code)
        
        # Try to auto-detect entry filter by fields
        detected_entry_code = self._detect_entry_filter(filter_dict)
        if detected_entry_code:
            return self._parse_entry_filter(filter_dict, detected_entry_code)
        
        # Default to raw dictionary (will be handled by condition resolver)
        return filter_dict
    
    def _detect_entry_filter(self, filter_dict: dict) -> str | None:
        """Detect entry filter type based on fields present in filter_dict"""
        filter_fields = set(filter_dict.keys()) - {"and", "or"}  # Exclude logical operators
        
        best_match = None
        best_score = 0
        
        for entry_code, filter_class in self._entry_filter_registry.items():
            # Get field names from the filter class
            try:
                # Create dummy instance to get field names
                dummy_instance = filter_class()
                class_fields = set(dummy_instance.model_fields.keys()) - {"and_", "or_"}
                
                # Calculate match score - how many fields match
                matching_fields = filter_fields & class_fields
                score = len(matching_fields) / max(len(filter_fields), 1)
                
                # If all filter_dict fields match class fields, it's a good candidate
                if matching_fields == filter_fields and score > best_score:
                    best_match = entry_code
                    best_score = score
                    
            except Exception:
                # Skip if can't create dummy instance
                continue
        
        return best_match
    
    def _parse_entry_filter(self, filter_dict: dict, entry_code: str) -> BaseEntryFilter:
        """Parse entry-specific filter"""
        filter_class = self._entry_filter_registry[entry_code]
        
        # Clean up the data for Pydantic validation
        cleaned_data = {}
        
        for key, value in filter_dict.items():
            if key in ["and", "or"]:
                # Handle nested filters
                if isinstance(value, list):
                    cleaned_data[key] = [
                        self._parse_dict_filter(item, entry_code) 
                        for item in value
                    ]
            else:
                cleaned_data[key] = value
        
        return filter_class(**cleaned_data)
    
    def _parse_combined_filter(self, filter_dict: dict, entry_code: str | None = None) -> CombinedFilter:
        """Parse combined filter (AND/OR)"""
        filters = []
        
        if "and" in filter_dict:
            for sub_filter_data in filter_dict["and"]:
                sub_filter = self._parse_dict_filter(sub_filter_data, entry_code)
                if sub_filter:
                    filters.append(sub_filter)
            return CombinedFilter(operator="and", filters=filters)
        
        elif "or" in filter_dict:
            for sub_filter_data in filter_dict["or"]:
                sub_filter = self._parse_dict_filter(sub_filter_data, entry_code)
                if sub_filter:
                    filters.append(sub_filter)
            return CombinedFilter(operator="or", filters=filters)
        
        else:
            raise ValueError("Combined filter must have 'and' or 'or' key")
    
    def _parse_not_filter(self, filter_dict: dict, entry_code: str | None = None) -> NotFilter:
        """Parse NOT filter"""
        if "not" not in filter_dict:
            raise ValueError("NOT filter must have 'not' key")
        
        sub_filter = self._parse_dict_filter(filter_dict["not"], entry_code)
        if not sub_filter:
            raise ValueError("NOT filter cannot have empty sub-filter")
        
        return NotFilter(filter=sub_filter) 