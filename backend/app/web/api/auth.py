from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from uuid import UUID

from ..schema.auth import (
    Token, UserResponse, LogoutResponse,
    SendVerificationCodeRequest, SendVerificationCodeResponse,
    VerifyCodeRequest, VerifyCodeResponse, RegisterWithVerificationRequest
)
from ..schema.sessions import SessionResponse, SessionRevokeResponse
from ..auth import get_password_hash, verify_password
from ..auth.deps import TokenDep, TokenRepositoryDep, UserRepositoryDep, UserDep
from ..deps import AnimestarsUserRepoDep, VerificationServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-verification", response_model=SendVerificationCodeResponse)
async def send_verification_code(
    request: SendVerificationCodeRequest,
    animestars_user_repo: AnimestarsUserRepoDep,
    verification_service: VerificationServiceDep,
):
    """Send verification code to username."""
    animestars_user = await animestars_user_repo.get_by_username(request.username)
    if animestars_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not found on Animestar",
        )
    
    await verification_service.create_and_send_code(request.username)
    
    return SendVerificationCodeResponse(
        message=f"Verification code sent to {request.username}"
    )


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(
    request: VerifyCodeRequest,
    verification_service: VerificationServiceDep,
):
    """Verify the provided code for the username."""
    is_valid = await verification_service.verify_code(request.username, request.code)
    
    if is_valid:
        return VerifyCodeResponse(
            success=True,
            message="Verification code verified successfully"
        )
    else:
        return VerifyCodeResponse(
            success=False,
            message="Invalid or expired verification code"
        )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: RegisterWithVerificationRequest,
    verification_service: VerificationServiceDep,
    user_repo: UserRepositoryDep,
    animestars_user_repo: AnimestarsUserRepoDep,
):
    """Register user with verification code."""
    # Check if username already exists
    db_user = await user_repo.get_user_by_username(user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
  
    animestars_user = await animestars_user_repo.get_by_username(user_data.username)
    if animestars_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not found on Animestar",
        )
    
    # Verify the code
    is_valid = await verification_service.mark_code_as_used(user_data.username, user_data.verification_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = await user_repo.create_user(user_data.username, hashed_password)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepositoryDep = None,
    token_repo: TokenRepositoryDep = None,
):
    # Authenticate user
    user = await user_repo.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = await token_repo.create(user_id=user.id)
    
    return {"access_token": token.get_access_token(), "token_type": "bearer"}


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    token: TokenDep,
    token_repo: TokenRepositoryDep,
):
    """
    Logout the current user.
    """
    await token_repo.deactivate_token(token.id)
    return LogoutResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserDep):
    return current_user


@router.get("/sessions", response_model=list[SessionResponse])
async def get_user_sessions(
    current_user: UserDep,
    token_repo: TokenRepositoryDep,
    current_token: TokenDep,
):
    """
    Get all active sessions for the current user.
    """
    sessions = await token_repo.get_active_sessions_by_user_id(current_user.id)
    return [
        SessionResponse(
            id=session.id,
            created_at=session.created_at,
            expire_at=session.expire_at,
            is_current=session.id == current_token.id
        )
        for session in sessions
    ]


@router.delete("/sessions/{session_id}", response_model=SessionRevokeResponse)
async def revoke_session(
    session_id: Annotated[str, Path(..., description="The ID of the session to revoke")],
    current_user: UserDep,
    token_repo: TokenRepositoryDep,
):
    """
    Revoke a specific session.
    """
    
    try:
        token_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    # Verify the session belongs to the current user
    session = await token_repo.get_token(token_uuid)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    await token_repo.deactivate_token(token_uuid)
    return SessionRevokeResponse(message="Session revoked successfully")
