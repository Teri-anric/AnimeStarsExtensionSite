from abc import ABC, abstractmethod
from fastapi import UploadFile


class BaseStorageService(ABC):
    """Abstract base class for file storage services."""
    
    @abstractmethod
    async def save(self, file: UploadFile, path: str) -> str:
        """
        Saves a file and returns the relative path to it.
        
        Args:
            file: Uploaded file
            path: Path for saving the file
            
        Returns:
            Relative path to the saved file
        """
        pass
    
    @abstractmethod
    def get_url(self, path: str) -> str:
        """
        Returns a public URL for accessing the file.
        
        Args:
            path: Relative path to the file
            
        Returns:
            Public URL for accessing the file
        """
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> None:
        """
        Deletes a file.
        
        Args:
            path: Relative path to the file to delete
        """
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """
        Checks if a file exists.
        
        Args:
            path: Relative path to the file
            
        Returns:
            True if the file exists, False otherwise
        """
        pass