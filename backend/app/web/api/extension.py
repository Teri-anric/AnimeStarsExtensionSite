from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any
import os
import logging
from pathlib import Path

from ..auth.deps import get_current_user
from ..auth.utils import verify_token
from ...database.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extension", tags=["extension"])
security = HTTPBearer()

# Path to the secrets file
SECRETS_DIR = Path(__file__).parent.parent.parent.parent.parent / "secrets"
ASS_API_TOKEN_FILE = SECRETS_DIR / "ass-api.txt"

def get_extension_token() -> str:
    """Read the ASS API token from secrets file."""
    try:
        if not ASS_API_TOKEN_FILE.exists():
            logger.error(f"ASS API token file not found: {ASS_API_TOKEN_FILE}")
            raise FileNotFoundError("Extension token file not found")
        
        with open(ASS_API_TOKEN_FILE, 'r', encoding='utf-8') as f:
            token = f.read().strip()
        
        if not token:
            logger.error("ASS API token file is empty")
            raise ValueError("Extension token is empty")
        
        logger.info("Extension token loaded successfully")
        return token
    
    except Exception as e:
        logger.error(f"Error reading extension token: {e}")
        raise


@router.get("/token")
async def get_extension_auth_token(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the extension authentication token for the current user.
    
    This endpoint provides the ASS API token from the secrets file
    to authenticated users for use in the browser extension.
    """
    try:
        # Verify user is authenticated
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Get the extension token
        extension_token = get_extension_token()
        
        logger.info(f"Extension token provided to user {current_user.username}")
        
        return {
            "success": True,
            "token": extension_token,
            "user_id": current_user.id,
            "username": current_user.username,
            "message": "Extension token retrieved successfully"
        }
    
    except FileNotFoundError:
        logger.error("Extension token file not found")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Extension token not available"
        )
    
    except ValueError as e:
        logger.error(f"Extension token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Extension token not valid"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error getting extension token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/verify")
async def verify_extension_connection(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify that the extension can connect with the provided token.
    
    This endpoint can be used by the frontend to test extension connectivity.
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Check if token file exists and is readable
        extension_token = get_extension_token()
        
        return {
            "success": True,
            "message": "Extension connection verified",
            "user_id": current_user.id,
            "username": current_user.username,
            "token_available": bool(extension_token)
        }
    
    except Exception as e:
        logger.error(f"Extension verification error: {e}")
        return {
            "success": False,
            "message": "Extension connection verification failed",
            "error": str(e),
            "token_available": False
        }


@router.get("/status")
async def get_extension_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the current extension integration status.
    """
    try:
        token_available = False
        token_error = None
        
        try:
            extension_token = get_extension_token()
            token_available = bool(extension_token)
        except Exception as e:
            token_error = str(e)
        
        return {
            "success": True,
            "extension": {
                "token_available": token_available,
                "token_error": token_error,
                "integration_enabled": token_available,
                "secrets_path": str(ASS_API_TOKEN_FILE.parent),
                "token_file_exists": ASS_API_TOKEN_FILE.exists()
            },
            "user": {
                "id": current_user.id if current_user else None,
                "username": current_user.username if current_user else None,
                "authenticated": bool(current_user)
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting extension status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve extension status"
        ) 