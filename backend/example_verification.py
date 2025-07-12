import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.parser.services import VerificationService


async def send_pm_message(username: str, message: str):
    """Приклад відправки PM повідомлення з автоматичним перелогіном."""
    try:
        from app.parser.repos.pm import AnimestarPMRepo
        from app.parser.repos.auth import AnimestarAuthRepo
        from app.parser.exception import PMError
        from app.config import settings
        
        repo = AnimestarPMRepo(settings.pm.cookie_file)
        result = await repo.send_pm(username, message)
        print(result)
    except PMError:
        print("Login failed, trying to login again")
        async with AnimestarAuthRepo(settings.pm.cookie_file) as auth_repo:
            await auth_repo.login(settings.pm.login, settings.pm.password)
        await send_pm_message(username, message)


async def example_verification_flow():
    """Приклад повного процесу верифікації."""
    username = "Teri"
    
    print(f"=== Приклад верифікації для користувача {username} ===")
    
    # 1. Відправка коду верифікації
    print("\n1. Відправка коду верифікації...")
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        code = await verification_service.create_and_send_code(username)
        print(f"Код {code} відправлено на користувача {username}")
    
    # 2. Верифікація коду
    print("\n2. Верифікація коду...")
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        is_valid = await verification_service.verify_code(username, code)
        
        if is_valid:
            print(f"✅ Код {code} успішно підтверджено!")
        else:
            print(f"❌ Код {code} невірний або застарів")
    
    # 3. Спроба повторної верифікації (має не вдатися)
    print("\n3. Спроба повторної верифікації...")
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        is_valid = await verification_service.verify_code(username, code)
        
        if is_valid:
            print(f"✅ Код {code} все ще дійсний")
        else:
            print(f"❌ Код {code} вже використано або застарів")
    
    # 4. Очищення застарілих кодів
    print("\n4. Очищення застарілих кодів...")
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        await verification_service.cleanup_expired_codes()
        print("✅ Застарілі коди видалено")


async def example_direct_pm():
    """Приклад прямого використання PM функціональності."""
    print("\n=== Приклад прямого використання PM ===")
    await send_pm_message("Teri", "Тестове повідомлення з нового сервісу!")


if __name__ == "__main__":
    # Запуск прикладів
    asyncio.run(example_verification_flow())
    asyncio.run(example_direct_pm())