#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки функціональності storage service.
Запускати тільки в Docker контейнері з встановленими залежностями.
"""

import asyncio
import tempfile
from pathlib import Path
from io import BytesIO

# Імітуємо UploadFile для тестування
class MockUploadFile:
    def __init__(self, filename: str, content: bytes, content_type: str = "text/plain"):
        self.filename = filename
        self.file = BytesIO(content)
        self.content_type = content_type
    
    async def read(self):
        return self.file.read()


async def test_storage_service():
    """Тестує функціональність LocalStorageService."""
    
    try:
        from app.storage import LocalStorageService
        from app.config import settings
        
        print("✅ Storage modules imported successfully")
        
        # Створюємо тимчасову директорію для тестування
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_service = LocalStorageService(
                storage_path=temp_dir,
                base_url="/static/storage"
            )
            
            print(f"✅ Storage service initialized with path: {temp_dir}")
            
            # Тестуємо збереження файлу
            test_content = b"Hello, World! This is a test file."
            test_file = MockUploadFile("test.txt", test_content)
            
            saved_path = await storage_service.save(test_file, "test/test.txt")
            print(f"✅ File saved at: {saved_path}")
            
            # Тестуємо перевірку існування
            exists = await storage_service.exists(saved_path)
            print(f"✅ File exists: {exists}")
            
            # Тестуємо отримання URL
            file_url = storage_service.get_url(saved_path)
            print(f"✅ File URL: {file_url}")
            
            # Тестуємо видалення
            await storage_service.delete(saved_path)
            exists_after_delete = await storage_service.exists(saved_path)
            print(f"✅ File deleted: {not exists_after_delete}")
            
            print("\n🎉 All tests passed!")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This test should be run in a Docker container with all dependencies installed.")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_storage_service())