# Файлове сховище

Цей модуль забезпечує функціональність для завантаження, зберігання та управління файлами в додатку.

## Архітектура

Система побудована на модульній архітектурі з абстрактним базовим класом `BaseStorageService`, що дозволяє легко замінювати реалізацію сховища (наприклад, перейти з локального на хмарне сховище).

### Компоненти

- **`BaseStorageService`** - абстрактний базовий клас з методами для роботи з файлами
- **`LocalStorageService`** - реалізація локального файлового сховища
- **API ендпоінти** - REST API для завантаження та видалення файлів

## Конфігурація

Налаштування сховища знаходяться в `app/config.py`:

```python
class StorageSettings(BaseSettings):
    path: str = "/storage"           # Шлях до директорії зберігання
    base_url: str = "/static/storage"  # Базовий URL для доступу
```

## API Ендпоінти

### Завантаження файлу

**POST** `/api/files/upload`

Завантажує файл на сервер. Потребує автентифікації.

**Параметри:**
- `file` (multipart/form-data) - файл для завантаження

**Обмеження:**
- Максимальний розмір файлу: 10MB

**Відповідь:**
```json
{
    "success": true,
    "file_url": "/static/storage/2024/01/15/uuid-filename.jpg",
    "file_path": "2024/01/15/uuid-filename.jpg",
    "filename": "original-filename.jpg",
    "size": 12345,
    "content_type": "image/jpeg"
}
```

### Видалення файлу

**DELETE** `/api/files/{file_path}`

Видаляє файл з сервера. Потребує автентифікації.

**Параметри:**
- `file_path` (path) - відносний шлях до файлу

**Відповідь:**
```json
{
    "success": true,
    "message": "Файл успішно видалено"
}
```

## Структура зберігання

Файли зберігаються в ієрархічній структурі за датою:

```
/storage/
├── 2024/
│   ├── 01/
│   │   ├── 15/
│   │   │   ├── uuid1-image.jpg
│   │   │   └── uuid2-document.pdf
│   │   └── 16/
│   │       └── uuid3-avatar.png
│   └── 02/
│       └── 01/
│           └── uuid4-file.txt
```

## Docker інтеграція

Файли зберігаються в іменованому Docker volume `local_storage`, що гарантує їх збереження при перезапуску контейнерів.

### Налаштування в docker-compose.yaml:

```yaml
services:
  backend:
    volumes:
      - local_storage:/storage

volumes:
  local_storage:
```

## Використання в коді

### Ін'єкція залежності

```python
from app.web.deps import StorageServiceDep

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    storage_service: StorageServiceDep = Depends()
):
    # Використання storage_service
    saved_path = await storage_service.save(file, "path/to/file")
    file_url = storage_service.get_url(saved_path)
```

### Пряме використання

```python
from app.storage import LocalStorageService

storage_service = LocalStorageService()
saved_path = await storage_service.save(file, "path/to/file")
```

## Розширення

Для додавання нових типів сховища (наприклад, Amazon S3):

1. Створіть новий клас, що наслідується від `BaseStorageService`
2. Реалізуйте всі абстрактні методи
3. Оновіть залежність `get_storage_service` в `app/web/deps.py`

## Тестування

Для тестування функціональності використовуйте:

```bash
# В Docker контейнері
python test_storage.py
```

## Безпека

- Всі ендпоінти потребують автентифікації
- Файли зберігаються з унікальними іменами (UUID)
- Обмеження на розмір файлів
- Валідація типів файлів (можна додати)