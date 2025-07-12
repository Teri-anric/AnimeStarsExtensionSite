# Зміни з додаванням репозиторію для VerificationCode

## Оновлення моделі

### До:
```python
class VerificationCode(UUIDPKMixin, TimestampMixin, Base):
    # Використовував TimestampMixin (created_at + updated_at)
```

### Після:
```python
class VerificationCode(UUIDPKMixin, Base):
    # Використовує тільки created_at
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
```

## Новий репозиторій

### Файл: `backend/app/database/repos/verification_code.py`

#### Основні методи:
- `create(username, code, expire_at)` - створення коду
- `get_by_username_and_code(username, code)` - отримання за username та code
- `get_active_by_username(username)` - всі активні коди користувача
- `deactivate_by_username(username)` - деактивація всіх кодів користувача
- `mark_as_used(verification_code_id)` - позначення як використаний
- `deactivate_expired_codes()` - деактивація застарілих кодів
- `delete_expired_codes()` - видалення застарілих кодів
- `get_valid_code(username, code)` - отримання валідного коду
- `cleanup_old_codes(days_old)` - очищення старих кодів
- `get_stats()` - статистика по кодах

## Оновлений сервіс

### Файл: `backend/app/parser/services/verification_service.py`

#### Зміни:
- Використовує `VerificationCodeRepository` замість прямих SQL запитів
- Додано нові методи:
  - `delete_expired_codes()` - видалення застарілих кодів
  - `cleanup_old_codes(days_old)` - очищення старих кодів
  - `get_stats()` - отримання статистики

## Нові API ендпоінти

### Файл: `backend/app/web/api/verification.py`

#### Додано:
- `POST /api/verification/delete-expired` - видалення застарілих кодів
- `POST /api/verification/cleanup-old` - очищення старих кодів
- `GET /api/verification/stats` - отримання статистики

## Оновлені CLI команди

### Файл: `backend/app/cli/verification.py`

#### Додано:
- `delete-expired` - видалення застарілих кодів
- `cleanup-old --days N` - очищення кодів старіше N днів
- `stats` - отримання статистики

## Оновлена міграція

### Файл: `backend/migration/versions/2025_01_15_1200_add_verification_codes_table.py`

#### Зміни:
- Видалено поле `updated_at`
- Залишено тільки `created_at`

## Переваги нової архітектури

### 1. **Розділення відповідальності**
- Репозиторій відповідає за роботу з БД
- Сервіс відповідає за бізнес-логіку
- API відповідає за HTTP інтерфейс

### 2. **Повторне використання**
- Репозиторій можна використовувати в різних сервісах
- Легко тестувати окремі компоненти

### 3. **Розширена функціональність**
- Статистика по кодах
- Гнучкі операції очищення
- Пряме управління через репозиторій

### 4. **Кращий контроль**
- Можна деактивувати коди без видалення
- Можна видаляти коди повністю
- Можна очищати старі коди

## Приклади використання

### Пряме використання репозиторію:
```python
from app.database.repos import VerificationCodeRepository

async with get_async_session() as session:
    repo = VerificationCodeRepository(session)
    
    # Створення коду
    code = await repo.create("user", "123456", expire_at)
    
    # Отримання валідного коду
    valid_code = await repo.get_valid_code("user", "123456")
    
    # Статистика
    stats = await repo.get_stats()
```

### Використання через сервіс:
```python
from app.parser.services import VerificationService

async with get_async_session() as session:
    service = VerificationService(session)
    
    # Відправка коду
    code = await service.create_and_send_code("user")
    
    # Верифікація
    is_valid = await service.verify_code("user", code)
    
    # Статистика
    stats = await service.get_stats()
```

## Міграція зі старої версії

1. **Оновіть імпорти** - використовуйте `VerificationCodeRepository`
2. **Замініть прямі SQL запити** на методи репозиторію
3. **Використовуйте нові методи сервісу** для розширеної функціональності
4. **Запустіть міграцію** для оновлення структури БД

## Тестування

```bash
# Тест з репозиторієм
python example_with_repo.py

# CLI команди
python -m app.cli.verification stats
python -m app.cli.verification cleanup-old --days 7

# API тести
curl -X GET "http://localhost:8000/api/verification/stats"
curl -X POST "http://localhost:8000/api/verification/delete-expired"
```