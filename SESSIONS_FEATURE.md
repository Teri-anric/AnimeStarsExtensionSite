# Session Management Feature

## Overview
This document describes the session management feature that allows users to view and revoke their active sessions.

## Backend Implementation

### New API Endpoints

#### 1. Get User Sessions
- **Endpoint**: `GET /api/auth/sessions`
- **Description**: Returns all active sessions for the current user
- **Authentication**: Required
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
- **Parameters**: `session_id` (UUID)
- **Response**:
```json
{
  "message": "Session revoked successfully"
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

## Testing

### Backend Tests
1. Test session creation during login
2. Test session retrieval
3. Test session revocation
4. Test session expiration

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

## Future Enhancements

1. **Session Analytics**: Track session usage patterns
2. **Device Information**: Show device/browser information for each session
3. **Bulk Operations**: Allow revoking multiple sessions at once
4. **Session Notifications**: Notify users of suspicious session activity

## Current Status

- ✅ Backend API endpoints implemented
- ✅ Database models updated
- ✅ Frontend components created
- ✅ Styling implemented
- ⏳ Backend deployment pending
- ⏳ Frontend API client regeneration pending
- ⏳ Testing and validation pending

## Notes

- The frontend currently shows a "Feature Coming Soon" message until the backend endpoints are deployed
- Once the backend is deployed, regenerate the API client to include the new endpoints
- Update the SessionsPage component to use the actual API calls instead of the placeholder