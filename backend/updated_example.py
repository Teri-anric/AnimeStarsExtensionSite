import asyncio

from app.parser.services import VerificationService
from app.database.connection import get_async_session
from app.config import settings


async def send_verification_code(username: str):
    """Відправка коду верифікації користувачу."""
    try:
        async with get_async_session() as session:
            verification_service = VerificationService(session)
            code = await verification_service.create_and_send_code(username)
            print(f"Код верифікації {code} відправлено на користувача {username}")
            return code
    except Exception as e:
        print(f"Помилка при відправці коду: {e}")
        return None


async def verify_user_code(username: str, code: str):
    """Верифікація коду користувача."""
    try:
        async with get_async_session() as session:
            verification_service = VerificationService(session)
            is_valid = await verification_service.verify_code(username, code)
            
            if is_valid:
                print(f"✅ Код {code} успішно підтверджено для користувача {username}")
                return True
            else:
                print(f"❌ Код {code} невірний або застарів для користувача {username}")
                return False
    except Exception as e:
        print(f"Помилка при верифікації коду: {e}")
        return False


async def cleanup_expired_codes():
    """Очищення застарілих кодів."""
    try:
        async with get_async_session() as session:
            verification_service = VerificationService(session)
            await verification_service.cleanup_expired_codes()
            print("✅ Застарілі коди успішно видалено")
    except Exception as e:
        print(f"Помилка при очищенні кодів: {e}")


async def main():
    """Основний приклад використання."""
    username = "Teri"
    
    print("=== Система верифікації з одноразовими кодами ===")
    print(f"Налаштування:")
    print(f"  - Cookie файл: {settings.pm.cookie_file}")
    print(f"  - Логін: {settings.pm.login}")
    print(f"  - Термін дії коду: {settings.pm.code_expire_hours} години")
    print()
    
    # 1. Відправка коду верифікації
    print("1. Відправка коду верифікації...")
    code = await send_verification_code(username)
    
    if code:
        # 2. Верифікація коду
        print("\n2. Верифікація коду...")
        is_valid = await verify_user_code(username, code)
        
        if is_valid:
            # 3. Спроба повторної верифікації (має не вдатися)
            print("\n3. Спроба повторної верифікації...")
            await verify_user_code(username, code)
    
    # 4. Очищення застарілих кодів
    print("\n4. Очищення застарілих кодів...")
    await cleanup_expired_codes()


if __name__ == "__main__":
    asyncio.run(main())