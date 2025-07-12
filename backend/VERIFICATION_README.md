# Система верифікації з одноразовими кодами

Ця система дозволяє відправляти одноразові коди верифікації користувачам через PM (приватні повідомлення) на Animestar.

## Функціональність

- ✅ Генерація 6-значних одноразових кодів
- ✅ Відправка кодів через PM з автоматичним перелогіном
- ✅ Зберігання кодів в базі даних з терміном дії
- ✅ Верифікація кодів з автоматичним позначенням як використаних
- ✅ API ендпоінти для інтеграції
- ✅ CLI команди для управління
- ✅ Автоматичне очищення застарілих кодів

## Конфігурація

Додайте наступні налаштування до вашого `.env` файлу:

```env
# PM налаштування
PM__COOKIE_FILE=cookie.json
PM__LOGIN=teri-test
PM__PASSWORD=testtest
PM__CODE_EXPIRE_HOURS=1
```

### Параметри конфігурації

- `PM__COOKIE_FILE` - файл для зберігання cookies (за замовчуванням: "cookie.json")
- `PM__LOGIN` - логін для авторизації на Animestar
- `PM__PASSWORD` - пароль для авторизації на Animestar
- `PM__CODE_EXPIRE_HOURS` - термін дії коду в годинах (за замовчуванням: 1)

## Використання

### 1. Через API

#### Відправка коду верифікації
```bash
curl -X POST "http://localhost:8000/api/verification/send-code" \
     -H "Content-Type: application/json" \
     -d '{"username": "Teri"}'
```

#### Верифікація коду
```bash
curl -X POST "http://localhost:8000/api/verification/verify-code" \
     -H "Content-Type: application/json" \
     -d '{"username": "Teri", "code": "123456"}'
```

#### Очищення застарілих кодів
```bash
curl -X POST "http://localhost:8000/api/verification/cleanup"
```

### 2. Через CLI

```bash
# Відправка коду
python -m app.cli.verification send Teri

# Верифікація коду
python -m app.cli.verification verify Teri 123456

# Деактивація застарілих кодів
python -m app.cli.verification cleanup

# Видалення застарілих кодів
python -m app.cli.verification delete-expired

# Очищення старих кодів (старіше 7 днів)
python -m app.cli.verification cleanup-old --days 7

# Отримання статистики
python -m app.cli.verification stats
```

### 3. Програмно

#### Використання сервісу:
```python
import asyncio
from app.database.connection import get_async_session
from app.parser.services import VerificationService

async def example():
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        
        # Відправка коду
        code = await verification_service.create_and_send_code("Teri")
        print(f"Код відправлено: {code}")
        
        # Верифікація коду
        is_valid = await verification_service.verify_code("Teri", code)
        print(f"Код валідний: {is_valid}")
        
        # Отримання статистики
        stats = await verification_service.get_stats()
        print(f"Статистика: {stats}")

asyncio.run(example())
```

#### Пряме використання репозиторію:
```python
import asyncio
from datetime import datetime, UTC
from app.database.connection import get_async_session
from app.database.repos import VerificationCodeRepository

async def example_repository():
    async with get_async_session() as session:
        repo = VerificationCodeRepository(session)
        
        # Створення коду
        code = await repo.create("Teri", "123456", datetime.now(UTC))
        
        # Отримання валідного коду
        valid_code = await repo.get_valid_code("Teri", "123456")
        
        # Позначення як використаний
        if valid_code:
            await repo.mark_as_used(str(valid_code.id))
        
        # Статистика
        stats = await repo.get_stats()
        print(f"Статистика: {stats}")

asyncio.run(example_repository())
```

## Структура бази даних

### Таблиця `verification_codes`

| Поле | Тип | Опис |
|------|-----|------|
| `id` | UUID | Унікальний ідентифікатор |
| `username` | String | Ім'я користувача |
| `code` | String | 6-значний код верифікації |
| `expire_at` | DateTime | Час закінчення дії коду |
| `is_used` | Boolean | Чи використано код |
| `is_active` | Boolean | Чи активний код |
| `created_at` | DateTime | Час створення |

## Безпека

- Коди генеруються криптографічно безпечно за допомогою `secrets.randbelow()`
- Коди автоматично позначаються як використані після першої верифікації
- Застарілі коди автоматично деактивуються
- Підтримується автоматичний перелогін при збої авторизації

## Міграція бази даних

Для створення таблиці `verification_codes` виконайте міграцію:

```bash
cd backend
python -m alembic upgrade head
```

## Приклад інтеграції в процес реєстрації

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_async_session
from app.parser.services import VerificationService

router = APIRouter()

@router.post("/register")
async def register_user(
    username: str,
    db: AsyncSession = Depends(get_async_session)
):
    # 1. Відправка коду верифікації
    verification_service = VerificationService(db)
    await verification_service.create_and_send_code(username)
    
    return {"message": "Код верифікації відправлено"}

@router.post("/confirm-registration")
async def confirm_registration(
    username: str,
    code: str,
    db: AsyncSession = Depends(get_async_session)
):
    # 2. Верифікація коду
    verification_service = VerificationService(db)
    is_valid = await verification_service.verify_code(username, code)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Невірний код")
    
    # 3. Створення користувача після успішної верифікації
    # ... логіка створення користувача
    
    return {"message": "Реєстрація підтверджена"}
```

## Обробка помилок

Система автоматично обробляє наступні помилки:

- **PMError** - автоматичний перелогін та повторна спроба відправки
- **RateLimitError** - обробка обмежень частоти запитів
- **LoginError** - помилки авторизації

## Тестування

Для тестування функціональності запустіть:

```bash
cd backend
# Основний приклад
python updated_example.py

# Приклад з репозиторієм
python example_with_repo.py

# CLI команди
python -m app.cli.verification stats
python -m app.cli.verification send Teri
```

Це запустить повні приклади роботи з системою верифікації.