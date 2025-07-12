import asyncio
from datetime import datetime, UTC

from app.database.connection import get_async_session
from app.parser.services import VerificationService
from app.database.repos import VerificationCodeRepository
from app.config import settings


async def example_with_repository():
    """Приклад використання з репозиторієм."""
    username = "Teri"
    
    print("=== Приклад використання з репозиторієм ===")
    print(f"Налаштування:")
    print(f"  - Cookie файл: {settings.pm.cookie_file}")
    print(f"  - Логін: {settings.pm.login}")
    print(f"  - Термін дії коду: {settings.pm.code_expire_hours} години")
    print()
    
    async with get_async_session() as session:
        # Створюємо репозиторій напряму
        repo = VerificationCodeRepository(session)
        
        # 1. Отримуємо статистику
        print("1. Отримання статистики...")
        stats = await repo.get_stats()
        print(f"📊 Поточна статистика: {stats}")
        
        # 2. Відправка коду через сервіс
        print("\n2. Відправка коду верифікації...")
        verification_service = VerificationService(session)
        code = await verification_service.create_and_send_code(username)
        print(f"✅ Код {code} відправлено на користувача {username}")
        
        # 3. Перевірка через репозиторій
        print("\n3. Перевірка коду через репозиторій...")
        verification_code = await repo.get_valid_code(username, code)
        if verification_code:
            print(f"✅ Код знайдено: {verification_code.code}")
            print(f"   Створено: {verification_code.created_at}")
            print(f"   Дійсний до: {verification_code.expire_at}")
            print(f"   Валідний: {verification_code.is_valid}")
        else:
            print("❌ Код не знайдено або не валідний")
        
        # 4. Верифікація через сервіс
        print("\n4. Верифікація коду...")
        is_valid = await verification_service.verify_code(username, code)
        if is_valid:
            print(f"✅ Код {code} успішно підтверджено!")
        else:
            print(f"❌ Код {code} невірний або застарів")
        
        # 5. Перевірка після використання
        print("\n5. Перевірка після використання...")
        verification_code_after = await repo.get_valid_code(username, code)
        if verification_code_after:
            print(f"⚠️  Код все ще доступний (не повинен бути)")
        else:
            print(f"✅ Код правильно позначений як використаний")
        
        # 6. Отримання всіх активних кодів для користувача
        print("\n6. Отримання активних кодів...")
        active_codes = await repo.get_active_by_username(username)
        print(f"📋 Активних кодів для {username}: {len(active_codes)}")
        for code_obj in active_codes:
            print(f"   - {code_obj.code} (створено: {code_obj.created_at})")
        
        # 7. Оновлена статистика
        print("\n7. Оновлена статистика...")
        updated_stats = await repo.get_stats()
        print(f"📊 Оновлена статистика: {updated_stats}")


async def example_direct_repository_usage():
    """Приклад прямого використання репозиторію."""
    print("\n=== Приклад прямого використання репозиторію ===")
    
    async with get_async_session() as session:
        repo = VerificationCodeRepository(session)
        
        # Створення коду вручну
        username = "TestUser"
        code = "123456"
        expire_at = datetime.now(UTC).replace(tzinfo=None)
        
        print(f"1. Створення коду для {username}...")
        verification_code = await repo.create(username, code, expire_at)
        print(f"✅ Код створено: {verification_code.id}")
        
        # Отримання коду
        print(f"2. Отримання коду...")
        found_code = await repo.get_by_username_and_code(username, code)
        if found_code:
            print(f"✅ Код знайдено: {found_code.code}")
        else:
            print("❌ Код не знайдено")
        
        # Позначення як використаний
        print(f"3. Позначення як використаний...")
        await repo.mark_as_used(str(verification_code.id))
        print("✅ Код позначений як використаний")
        
        # Перевірка валідності
        print(f"4. Перевірка валідності...")
        valid_code = await repo.get_valid_code(username, code)
        if valid_code:
            print("⚠️  Код все ще валідний (не повинен бути)")
        else:
            print("✅ Код правильно позначений як невалідний")


async def example_cleanup_operations():
    """Приклад операцій очищення."""
    print("\n=== Приклад операцій очищення ===")
    
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        
        # Деактивація застарілих кодів
        print("1. Деактивація застарілих кодів...")
        await verification_service.cleanup_expired_codes()
        print("✅ Застарілі коди деактивовано")
        
        # Видалення застарілих кодів
        print("2. Видалення застарілих кодів...")
        await verification_service.delete_expired_codes()
        print("✅ Застарілі коди видалено")
        
        # Очищення старих кодів
        print("3. Очищення кодів старіше 7 днів...")
        await verification_service.cleanup_old_codes(7)
        print("✅ Старі коди видалено")
        
        # Фінальна статистика
        print("4. Фінальна статистика...")
        stats = await verification_service.get_stats()
        print(f"📊 Фінальна статистика: {stats}")


if __name__ == "__main__":
    # Запуск всіх прикладів
    asyncio.run(example_with_repository())
    asyncio.run(example_direct_repository_usage())
    asyncio.run(example_cleanup_operations())