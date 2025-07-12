import asyncio
from app.database.connection import get_async_session
from app.parser.services import VerificationService

async def test_verification():
    async with get_async_session() as session:
        service = VerificationService(session)
        
        # Тест відправки коду
        code = await service.create_and_send_code("Teri")
        print(f"Код відправлено: {code}")
        
        # Тест верифікації
        is_valid = await service.verify_code("Teri", code)
        print(f"Код валідний: {is_valid}")

if __name__ == "__main__":
    asyncio.run(test_verification())