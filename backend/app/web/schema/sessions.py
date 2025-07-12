from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List


class SessionResponse(BaseModel):
    """Response model for a single session"""
    id: UUID
    created_at: datetime
    expire_at: datetime
    is_current: bool
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Response model for a list of sessions"""
    sessions: List[SessionResponse]
    
    class Config:
        from_attributes = True


class SessionRevokeResponse(BaseModel):
    """Response model for session revocation"""
    message: str


class SessionIdParam(BaseModel):
    """Parameter model for session ID validation"""
    session_id: UUID


class SessionError(BaseModel):
    """Error model for session-related errors"""
    detail: str
    error_code: str | None = None