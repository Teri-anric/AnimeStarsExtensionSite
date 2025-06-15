from typing import Dict, Optional
from .metadata_container import MetadataContainer


class MetadataProvider:
    """Provider that manages multiple metadata containers"""
    
    def __init__(self):
        self._containers: Dict[str, MetadataContainer] = {}
    
    def register_container(self, container: MetadataContainer) -> "MetadataProvider":
        """Register a metadata container"""
        self._containers[container.entity_code] = container
        return self
    
    def get_container(self, entity_code: str) -> Optional[MetadataContainer]:
        """Get metadata container by entity code"""
        return self._containers.get(entity_code)
    
    def has_container(self, entity_code: str) -> bool:
        """Check if container exists"""
        return entity_code in self._containers
    
    def get_all_containers(self) -> Dict[str, MetadataContainer]:
        """Get all registered containers"""
        return self._containers.copy()
    
    def get_container_or_raise(self, entity_code: str) -> MetadataContainer:
        """Get container or raise exception if not found"""
        container = self.get_container(entity_code)
        if container is None:
            raise ValueError(f"No metadata container found for entity code: {entity_code}")
        return container 