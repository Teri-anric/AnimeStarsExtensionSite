from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import Optional


class BaseStorageService(ABC):
    """Абстрактний базовий клас для сервісів файлового сховища."""
    
    @abstractmethod
    async def save(self, file: UploadFile, path: str) -> str:
        """
        Зберігає файл і повертає відносний шлях до нього.
        
        Args:
            file: Завантажений файл
            path: Шлях для збереження файлу
            
        Returns:
            Відносний шлях до збереженого файлу
        """
        pass
    
    @abstractmethod
    def get_url(self, path: str) -> str:
        """
        Повертає публічний URL для доступу до файлу.
        
        Args:
            path: Відносний шлях до файлу
            
        Returns:
            Публічний URL для доступу до файлу
        """
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> None:
        """
        Видаляє файл.
        
        Args:
            path: Відносний шлях до файлу для видалення
        """
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """
        Перевіряє чи існує файл.
        
        Args:
            path: Відносний шлях до файлу
            
        Returns:
            True якщо файл існує, False інакше
        """
        pass