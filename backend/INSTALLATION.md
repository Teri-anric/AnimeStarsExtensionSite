# Інструкції по встановленню системи верифікації

## Крок 1: Налаштування конфігурації

Додайте наступні змінні до вашого `.env` файлу:

```env
# PM налаштування для верифікації
PM__COOKIE_FILE=cookie.json
PM__LOGIN=teri-test
PM__PASSWORD=testtest
PM__CODE_EXPIRE_HOURS=1
```

## Крок 2: Запуск міграції бази даних

```bash
cd backend
python -m alembic upgrade head
```

Це створить таблицю `verification_codes` в базі даних.

## Крок 3: Тестування функціональності

### Тест через CLI:
```bash
cd backend
python -m app.cli.verification send Teri
```

### Тест через приклад:
```bash
cd backend
python updated_example.py
```

### Тест через API (якщо сервер запущений):
```bash
curl -X POST "http://localhost:8000/api/verification/send-code" \
     -H "Content-Type: application/json" \
     -d '{"username": "Teri"}'
```

## Крок 4: Інтеграція в ваш код

### Використання в процесі реєстрації:

```python
from app.parser.services import VerificationService
from app.database.connection import get_async_session

async def register_user(username: str):
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        
        # Відправка коду верифікації
        code = await verification_service.create_and_send_code(username)
        print(f"Код {code} відправлено на {username}")
        
        return {"message": "Код верифікації відправлено"}

async def confirm_registration(username: str, code: str):
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        
        # Верифікація коду
        is_valid = await verification_service.verify_code(username, code)
        
        if is_valid:
            # Створення користувача після успішної верифікації
            # ... ваш код створення користувача
            return {"message": "Реєстрація підтверджена"}
        else:
            return {"error": "Невірний код верифікації"}
```

## Структура файлів

```
backend/
├── app/
│   ├── config.py                    # Оновлений конфіг з PM налаштуваннями
│   ├── database/
│   │   └── models/
│   │       ├── __init__.py          # Оновлений з VerificationCode
│   │       └── verification_code.py # Нова модель
│   ├── parser/
│   │   └── services/
│   │       ├── __init__.py          # Експорт VerificationService
│   │       └── verification_service.py # Основний сервіс
│   └── web/
│       └── api/
│           ├── __init__.py          # Оновлений з verification_router
│           └── verification.py      # API ендпоінти
├── migration/
│   └── versions/
│       └── 2025_01_15_1200_add_verification_codes_table.py # Міграція
├── app/cli/
│   └── verification.py              # CLI команди
├── example_verification.py          # Детальний приклад
├── updated_example.py               # Спрощений приклад
├── VERIFICATION_README.md           # Повна документація
└── INSTALLATION.md                  # Цей файл
```

## Перевірка роботи

1. **Перевірте конфігурацію:**
   ```bash
   cd backend
   python -c "from app.config import settings; print(f'PM settings: {settings.pm}')"
   ```

2. **Запустіть тест:**
   ```bash
   python updated_example.py
   ```

3. **Перевірте API (якщо запущений):**
   ```bash
   curl -X POST "http://localhost:8000/api/verification/send-code" \
        -H "Content-Type: application/json" \
        -d '{"username": "Teri"}'
   ```

## Вирішення проблем

### Помилка "Login failed"
- Перевірте правильність логіну та пароля в `.env`
- Переконайтеся, що файл `cookie.json` доступний для запису

### Помилка "Database connection"
- Перевірте налаштування бази даних
- Запустіть міграції: `python -m alembic upgrade head`

### Помилка "PMError"
- Перевірте підключення до Animestar
- Переконайтеся, що логін/пароль дійсні

## Додаткові можливості

- **Автоматичне очищення:** Запустіть `python -m app.cli.verification cleanup`
- **Налаштування терміну дії:** Змініть `PM__CODE_EXPIRE_HOURS` в `.env`
- **Кастомні повідомлення:** Відредагуйте `verification_service.py`

## Підтримка

Для отримання допомоги звертайтеся до `VERIFICATION_README.md` або запустіть:
```bash
python -m app.cli.verification --help
```