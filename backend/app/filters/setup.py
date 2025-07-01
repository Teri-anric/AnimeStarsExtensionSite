from .service import FilterService

# Global filter service instance
default_filter_service = FilterService()

def get_filter_service() -> FilterService:
    """Get the default filter service instance"""
    return default_filter_service 