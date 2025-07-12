from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db
from ...parser.services import VerificationService


router = APIRouter(prefix="/verification", tags=["verification"])


class SendCodeRequest(BaseModel):
    username: str


class VerifyCodeRequest(BaseModel):
    username: str
    code: str


class SendCodeResponse(BaseModel):
    message: str


class VerifyCodeResponse(BaseModel):
    success: bool
    message: str


@router.post("/send-code", response_model=SendCodeResponse)
async def send_verification_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a verification code to the specified username via PM."""
    try:
        verification_service = VerificationService(db)
        await verification_service.create_and_send_code(request.username)
        
        return SendCodeResponse(
            message=f"Код верифікації відправлено на користувача {request.username}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при відправці коду: {str(e)}"
        )


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify the provided code for the username."""
    try:
        verification_service = VerificationService(db)
        is_valid = await verification_service.verify_code(request.username, request.code)
        
        if is_valid:
            return VerifyCodeResponse(
                success=True,
                message="Код верифікації успішно підтверджено"
            )
        else:
            return VerifyCodeResponse(
                success=False,
                message="Невірний код верифікації або код застарів"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при верифікації коду: {str(e)}"
        )


@router.post("/cleanup", response_model=dict)
async def cleanup_expired_codes(
    db: AsyncSession = Depends(get_db)
):
    """Clean up expired verification codes."""
    try:
        verification_service = VerificationService(db)
        await verification_service.cleanup_expired_codes()
        
        return {"message": "Застарілі коди успішно видалено"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при очищенні кодів: {str(e)}"
        )