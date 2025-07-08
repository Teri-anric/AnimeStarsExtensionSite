from fastapi import APIRouter, Depends, HTTPException, status
import logging

from ..auth.deps import get_current_user
from ...database.repos.user import TokenRepository
from ...database.models.user import User
from ..schema.auth import Token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extension", tags=["extension"])


@router.post("/token", response_model=Token)
async def get_extension_token(
    current_user: User = Depends(get_current_user),
    token_repo: TokenRepository = Depends(lambda: TokenRepository())
) -> Token:
    """
    Generate a new authentication token for the browser extension.
    
    This endpoint creates a new token using the same system as regular user login,
    allowing the extension to authenticate API requests on behalf of the user.
    """
    try:
        # Verify user is authenticated
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Create a new token for the user (same as login)
        token = await token_repo.create_token(current_user.id)
        
        logger.info(f"Extension token created for user {current_user.username}")
        
        return {
            "access_token": token.get_access_token(),
            "token_type": "bearer"
        }
    
    except Exception as e:
        logger.error(f"Error creating extension token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create extension token"
        ) 