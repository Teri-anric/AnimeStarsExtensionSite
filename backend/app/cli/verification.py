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
        print("Застарілі коди успішно видалено")


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
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up expired codes")
    
    args = parser.parse_args()
    
    if args.command == "send":
        asyncio.run(send_verification_code(args.username))
    elif args.command == "verify":
        asyncio.run(verify_code(args.username, args.code))
    elif args.command == "cleanup":
        asyncio.run(cleanup_expired_codes())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()