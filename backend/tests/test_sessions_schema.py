import pytest
from datetime import datetime, timezone
from uuid import uuid4
from app.web.schema.sessions import (
    SessionResponse,
    SessionListResponse,
    SessionRevokeResponse,
    SessionIdParam,
    SessionError,
)


class TestSessionResponse:
    def test_session_response_creation(self):
        """Test creating a SessionResponse instance"""
        session_id = uuid4()
        created_at = datetime.now(timezone.utc)
        expire_at = datetime.now(timezone.utc)
        
        session = SessionResponse(
            id=session_id,
            created_at=created_at,
            expire_at=expire_at,
            is_current=True
        )
        
        assert session.id == session_id
        assert session.created_at == created_at
        assert session.expire_at == expire_at
        assert session.is_current is True

    def test_session_response_from_orm(self):
        """Test creating SessionResponse from ORM model"""
        session_id = uuid4()
        created_at = datetime.now(timezone.utc)
        expire_at = datetime.now(timezone.utc)
        
        # Mock ORM model
        class MockSession:
            def __init__(self):
                self.id = session_id
                self.created_at = created_at
                self.expire_at = expire_at
        
        mock_session = MockSession()
        session = SessionResponse.model_validate(mock_session)
        
        assert session.id == session_id
        assert session.created_at == created_at
        assert session.expire_at == expire_at


class TestSessionListResponse:
    def test_session_list_response_creation(self):
        """Test creating a SessionListResponse instance"""
        session_id = uuid4()
        created_at = datetime.now(timezone.utc)
        expire_at = datetime.now(timezone.utc)
        
        session = SessionResponse(
            id=session_id,
            created_at=created_at,
            expire_at=expire_at,
            is_current=True
        )
        
        session_list = SessionListResponse(sessions=[session])
        
        assert len(session_list.sessions) == 1
        assert session_list.sessions[0].id == session_id


class TestSessionRevokeResponse:
    def test_session_revoke_response_creation(self):
        """Test creating a SessionRevokeResponse instance"""
        message = "Session revoked successfully"
        response = SessionRevokeResponse(message=message)
        
        assert response.message == message


class TestSessionIdParam:
    def test_session_id_param_creation(self):
        """Test creating a SessionIdParam instance"""
        session_id = uuid4()
        param = SessionIdParam(session_id=session_id)
        
        assert param.session_id == session_id


class TestSessionError:
    def test_session_error_creation(self):
        """Test creating a SessionError instance"""
        detail = "Session not found"
        error_code = "SESSION_NOT_FOUND"
        
        error = SessionError(detail=detail, error_code=error_code)
        
        assert error.detail == detail
        assert error.error_code == error_code

    def test_session_error_without_code(self):
        """Test creating a SessionError instance without error_code"""
        detail = "Session not found"
        
        error = SessionError(detail=detail)
        
        assert error.detail == detail
        assert error.error_code is None