from .service import FilterService
from .metadata import default_metadata_provider
from .entries.card_filter import CardFilter
from .entries.desk_filter import DeckFilter


def create_default_filter_service() -> FilterService:
    """Create a default filter service with all standard configurations"""
    filter_service = FilterService(default_metadata_provider)
    filter_service.register_entry_filter(CardFilter)
    filter_service.register_entry_filter(DeckFilter)
    return filter_service


# Global default instance
default_filter_service = create_default_filter_service() 