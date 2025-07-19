import os
import aiofiles
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from typing import Optional

from .base import BaseStorageService


class LocalStorageService(BaseStorageService):
    """Local file storage implementation."""
    LOCAL_STORAGE_PATH = "/storage"
    LOCAL_STORAGE_URL = "/local/storage"
    CHUNK_SIZE = 8192
    
    def __init__(self, storage_path: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initializes local storage.
        
        Args:
            storage_path: Path to directory for storing files
            base_url: Base URL for accessing files
        """
        self.storage_path = Path(storage_path or self.LOCAL_STORAGE_PATH)
        self.base_url = base_url or self.LOCAL_STORAGE_URL
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def generate_path(self, upload_file: UploadFile) -> str:
        file_extension = Path(upload_file.filename).suffix if upload_file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        current_date = datetime.now().strftime("%Y/%m/%d")
        return f"{current_date}/{unique_filename}"
    
    
    async def save(self, file: UploadFile, path: str) -> str:
        """
        Saves a file locally.
        
        Args:
            file: Uploaded file
            path: Relative path for saving the file
            
        Returns:
            Relative path to the saved file
        """
        full_path = self.storage_path / path
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        fp = await aiofiles.open(full_path, 'wb')
        try:
            while chunk := await file.read(self.CHUNK_SIZE):
                await fp.write(chunk)
        finally:
            await fp.close()
        
        return path
    
    def get_url(self, path: str) -> str:
        """
        Returns a public URL for accessing the file.
        
        Args:
            path: Relative path to the file
            
        Returns:
            Public URL for accessing the file
        """
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
    
    async def delete(self, path: str) -> None:
        """
        Deletes a file.
        
        Args:
            path: Relative path to the file to delete
        """
        full_path = self.storage_path / path
        
        if await self.exists(path):
            os.remove(full_path)
    
    async def exists(self, path: str) -> bool:
        """
        Checks if a file exists.
        
        Args:
            path: Relative path to the file
            
        Returns:
            True if the file exists, False otherwise
        """
        full_path = self.storage_path / path
        return full_path.exists()