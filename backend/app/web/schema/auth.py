from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List


class UserBase(BaseModel):
    username: str


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    token_id: UUID | None = None
    user_id: UUID | None = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LogoutResponse(BaseModel):
    message: str


class AuthError(BaseModel):
    detail: str


class ValidationError(BaseModel):
    detail: str
    loc: List[str]
    msg: str
    type: str


class SendVerificationCodeRequest(BaseModel):
    username: str


class SendVerificationCodeResponse(BaseModel):
    message: str


class VerifyCodeRequest(BaseModel):
    username: str
    code: str


class VerifyCodeResponse(BaseModel):
    success: bool
    message: str


class RegisterWithVerificationRequest(BaseModel):
    username: str
    password: str
    verification_code: str
