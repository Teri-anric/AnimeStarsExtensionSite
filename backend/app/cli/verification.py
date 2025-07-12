import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_async_session
from ..parser.services import VerificationService


async def send_verification_code(username: str):
    """Send a verification code to the specified username."""
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        code = await verification_service.create_and_send_code(username)
        print(f"Код верифікації {code} відправлено на користувача {username}")


async def verify_code(username: str, code: str):
    """Verify the provided code for the username."""
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        is_valid = await verification_service.verify_code(username, code)
        
        if is_valid:
            print(f"Код {code} успішно підтверджено для користувача {username}")
        else:
            print(f"Код {code} невірний або застарів для користувача {username}")


async def cleanup_expired_codes():
    """Clean up expired verification codes."""
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        await verification_service.cleanup_expired_codes()
        print("✅ Застарілі коди успішно деактивовано")


async def delete_expired_codes():
    """Delete expired verification codes."""
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        await verification_service.delete_expired_codes()
        print("✅ Застарілі коди успішно видалено")


async def cleanup_old_codes(days_old: int = 7):
    """Clean up old verification codes."""
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        await verification_service.cleanup_old_codes(days_old)
        print(f"✅ Коди старіше {days_old} днів успішно видалено")


async def get_stats():
    """Get verification codes statistics."""
    async with get_async_session() as session:
        verification_service = VerificationService(session)
        stats = await verification_service.get_stats()
        print("📊 Статистика кодів верифікації:")
        print(f"  - Загальна кількість: {stats['total']}")
        print(f"  - Активні: {stats['active']}")
        print(f"  - Використані: {stats['used']}")
        print(f"  - Застарілі: {stats['expired']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Verification code management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Send code command
    send_parser = subparsers.add_parser("send", help="Send verification code")
    send_parser.add_argument("username", help="Username to send code to")
    
    # Verify code command
    verify_parser = subparsers.add_parser("verify", help="Verify code")
    verify_parser.add_argument("username", help="Username")
    verify_parser.add_argument("code", help="Verification code")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Deactivate expired codes")
    
    # Delete expired command
    delete_parser = subparsers.add_parser("delete-expired", help="Delete expired codes")
    
    # Cleanup old command
    cleanup_old_parser = subparsers.add_parser("cleanup-old", help="Clean up old codes")
    cleanup_old_parser.add_argument("--days", type=int, default=7, help="Days old (default: 7)")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get verification codes statistics")
    
    args = parser.parse_args()
    
    if args.command == "send":
        asyncio.run(send_verification_code(args.username))
    elif args.command == "verify":
        asyncio.run(verify_code(args.username, args.code))
    elif args.command == "cleanup":
        asyncio.run(cleanup_expired_codes())
    elif args.command == "delete-expired":
        asyncio.run(delete_expired_codes())
    elif args.command == "cleanup-old":
        asyncio.run(cleanup_old_codes(args.days))
    elif args.command == "stats":
        asyncio.run(get_stats())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()