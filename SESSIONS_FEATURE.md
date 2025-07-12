# Session Management Feature

## Overview
This document describes the session management feature that allows users to view and revoke their active sessions.

## Backend Implementation

### New API Endpoints

#### 1. Get User Sessions
- **Endpoint**: `GET /api/auth/sessions`
- **Description**: Returns all active sessions for the current user
- **Authentication**: Required
- **Response Model**: `List[SessionResponse]`
- **Response**:
```json
[
  {
    "id": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "expire_at": "2024-01-01T23:59:59Z",
    "is_current": true
  }
]
```

#### 2. Revoke Session
- **Endpoint**: `DELETE /api/auth/sessions/{session_id}`
- **Description**: Revokes a specific session
- **Authentication**: Required
- **Parameters**: `session_id` (UUID) - Path parameter
- **Response Model**: `SessionRevokeResponse`
- **Response**:
```json
{
  "message": "Session revoked successfully"
}
```

#### 3. Logout (Updated)
- **Endpoint**: `POST /api/auth/logout`
- **Description**: Logs out the current user by deactivating the session
- **Authentication**: Required
- **Response Model**: `LogoutResponse`
- **Response**:
```json
{
  "message": "Successfully logged out"
}
```

### Database Changes

#### Token Model Updates
The `Token` model in `backend/app/database/models/user.py` has been updated with:
- `is_active` field for session status
- `expire_at` field for session expiration
- `user_id` field for user association

#### Repository Updates
The `TokenRepository` in `backend/app/database/repos/user.py` has been updated with:
- `get_active_sessions_by_user_id()` method
- `get_token()` method
- `deactivate_token()` method

### Schema Definitions

#### New Schema Files

##### 1. `backend/app/web/schema/sessions.py`
Contains all session-related schemas:

- **SessionResponse**: Response model for a single session
- **SessionListResponse**: Response model for a list of sessions
- **SessionRevokeResponse**: Response model for session revocation
- **SessionIdParam**: Parameter model for session ID validation
- **SessionError**: Error model for session-related errors

##### 2. Updated `backend/app/web/schema/auth.py`
Added new auth-related schemas:

- **LogoutResponse**: Response model for logout endpoint
- **AuthError**: Error model for authentication errors
- **ValidationError**: Error model for validation errors

#### Schema Examples

```python
# Session Response
class SessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    expire_at: datetime
    is_current: bool
    
    class Config:
        from_attributes = True

# Session Revoke Response
class SessionRevokeResponse(BaseModel):
    message: str

# Logout Response
class LogoutResponse(BaseModel):
    message: str
```

## Frontend Implementation

### New Components

#### 1. SessionsPage
- **Location**: `frontend/src/pages/settings/SessionsPage.tsx`
- **Description**: Main page for viewing and managing sessions
- **Features**:
  - Display all active sessions
  - Show current session indicator
  - Revoke other sessions
  - Refresh sessions list

#### 2. Updated Header
- **Location**: `frontend/src/components/Header.tsx`
- **Changes**: Added "Sessions" link in user navigation

### Updated Components

#### 1. AuthContext
- **Location**: `frontend/src/context/AuthContext.tsx`
- **Changes**: 
  - Fixed logout function to properly call API
  - Added proper error handling

#### 2. ProtectedRoute
- **Location**: `frontend/src/components/ProtectedRoute.tsx`
- **Changes**: Added support for redirect after login

#### 3. LoginForm
- **Location**: `frontend/src/pages/auth/LoginForm.tsx`
- **Changes**: Added redirect support after successful login

### Styling
- **Location**: `frontend/src/styles/SessionsPage.css`
- **Features**: Modern, responsive design with proper visual feedback

## API Documentation

### Detailed Endpoint Documentation

All endpoints include comprehensive documentation with:
- Parameter descriptions
- Response models
- Error codes and messages
- Authentication requirements
- Usage examples

### Error Handling

The API includes proper error handling for:
- Invalid session ID format (400)
- Session not found (404)
- Unauthorized access (401)
- Validation errors (422)

## Testing

### Backend Tests
- **Location**: `backend/tests/test_sessions_schema.py`
- **Coverage**: Schema validation, response models, error handling
- **Test Cases**:
  - Session response creation
  - ORM model validation
  - Error response creation
  - Parameter validation

### Frontend Tests
1. Test session page loading
2. Test session revocation
3. Test redirect after login
4. Test logout functionality

## Security Considerations

1. **Session Validation**: Ensure only the session owner can revoke their sessions
2. **Token Security**: Implement proper token validation and expiration
3. **Rate Limiting**: Add rate limiting to session management endpoints
4. **Audit Logging**: Log session creation and revocation events
5. **Input Validation**: Validate all session IDs and parameters

## Deployment Steps

### Backend Deployment
1. Deploy the updated backend code with new API endpoints
2. Ensure database migrations are applied
3. Test the new endpoints:
   ```bash
   curl -H "Authorization: Bearer <token>" https://your-api.com/api/auth/sessions
   ```

### Frontend Deployment
1. Deploy the updated frontend code
2. Regenerate API client if needed:
   ```bash
   cd frontend
   npm run generate-api-client
   ```
3. Test the session management feature

## Future Enhancements

1. **Session Analytics**: Track session usage patterns
2. **Device Information**: Show device/browser information for each session
3. **Bulk Operations**: Allow revoking multiple sessions at once
4. **Session Notifications**: Notify users of suspicious session activity
5. **Session Expiration Warnings**: Warn users before sessions expire

## Current Status

- ✅ Backend API endpoints implemented
- ✅ Database models updated
- ✅ Schema definitions created
- ✅ API documentation added
- ✅ Error handling implemented
- ✅ Frontend components created
- ✅ Styling implemented
- ✅ Test cases created
- ⏳ Backend deployment pending
- ⏳ Frontend API client regeneration pending
- ⏳ Integration testing pending

## Notes

- The frontend currently shows a "Feature Coming Soon" message until the backend endpoints are deployed
- Once the backend is deployed, regenerate the API client to include the new endpoints
- Update the SessionsPage component to use the actual API calls instead of the placeholder
- All schemas include proper validation and documentation
- Error responses are standardized across all endpoints