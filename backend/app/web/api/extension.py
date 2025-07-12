from fastapi import APIRouter, Depends, HTTPException, status
import logging

from ..auth.deps import UserDep, ProtectedDep
from ...database.repos.user import TokenRepository
from ..schema.auth import Token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extension", tags=["extension"], dependencies=[ProtectedDep])


@router.post("/token", response_model=Token)
async def get_extension_token(
    current_user: UserDep,
    token_repo: TokenRepository = Depends(lambda: TokenRepository())
) -> Token:
    """
    Generate a new authentication token for the browser extension.
    
    This endpoint creates a new token using the same system as regular user login,
    allowing the extension to authenticate API requests on behalf of the user.
    """
    try:
        token = await token_repo.create(user_id=current_user.id, expire_at=None)
        
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