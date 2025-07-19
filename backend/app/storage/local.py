import os
import aiofiles
from pathlib import Path
from fastapi import UploadFile
from typing import Optional

from .base import BaseStorageService
from app.config import settings


class LocalStorageService(BaseStorageService):
    """Реалізація локального файлового сховища."""
    
    def __init__(self, storage_path: Optional[str] = None, base_url: Optional[str] = None):
        """
        Ініціалізує локальне сховище.
        
        Args:
            storage_path: Шлях до директорії для зберігання файлів
            base_url: Базовий URL для доступу до файлів
        """
        self.storage_path = Path(storage_path or settings.storage.path)
        self.base_url = base_url or settings.storage.base_url
        
        # Створюємо директорію якщо вона не існує
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def save(self, file: UploadFile, path: str) -> str:
        """
        Зберігає файл локально.
        
        Args:
            file: Завантажений файл
            path: Відносний шлях для збереження файлу
            
        Returns:
            Відносний шлях до збереженого файлу
        """
        # Створюємо повний шлях до файлу
        full_path = self.storage_path / path
        
        # Створюємо директорію якщо вона не існує
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Зберігаємо файл
        async with aiofiles.open(full_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return path
    
    def get_url(self, path: str) -> str:
        """
        Повертає публічний URL для доступу до файлу.
        
        Args:
            path: Відносний шлях до файлу
            
        Returns:
            Публічний URL для доступу до файлу
        """
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
    
    async def delete(self, path: str) -> None:
        """
        Видаляє файл.
        
        Args:
            path: Відносний шлях до файлу для видалення
        """
        full_path = self.storage_path / path
        
        if await self.exists(path):
            os.remove(full_path)
    
    async def exists(self, path: str) -> bool:
        """
        Перевіряє чи існує файл.
        
        Args:
            path: Відносний шлях до файлу
            
        Returns:
            True якщо файл існує, False інакше
        """
        full_path = self.storage_path / path
        return full_path.exists()