from .service import FilterService
from .metadata import CardMetadataContainer, SummaryCardUsersMetadataContainer, MetadataProvider
from .entries.card_filter import CardFilter
from .entries.summary_card_users_filter import SummaryCardUsersFilter


def create_default_filter_service() -> FilterService:
    """Create a default filter service with all standard configurations"""
    # Create metadata provider
    metadata_provider = MetadataProvider()
    
    # Register metadata containers
    metadata_provider.register_container(CardMetadataContainer())
    metadata_provider.register_container(SummaryCardUsersMetadataContainer())
    
    # Create filter service
    filter_service = FilterService(metadata_provider)
    
    # Register entry filters
    filter_service.register_entry_filter(CardFilter)
    filter_service.register_entry_filter(SummaryCardUsersFilter)
    
    return filter_service


# Global default instance
default_filter_service = create_default_filter_service() 