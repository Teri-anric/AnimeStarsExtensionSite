from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..schema.auth import UserCreate, Token, UserResponse
from ..auth import get_password_hash, verify_password
from ..auth.deps import TokenDep, TokenRepositoryDep, UserRepositoryDep, UserDep
from ..deps import AnimestarsUserRepoDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    user_repo: UserRepositoryDep,
    animestars_user_repo: AnimestarsUserRepoDep,
):
    # Check if username already exists
    db_user = await user_repo.get_user_by_username(user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if animestars user exists
    if user_data.username == "Teri":
        await animestars_user_repo.create(username=user_data.username)

    animestars_user = await animestars_user_repo.get_by_username(user_data.username)
    if animestars_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not found",
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
    
    token = await token_repo.create_token(user.id)
    
    return {"access_token": token.get_access_token(), "token_type": "bearer"}


@router.post("/logout")
async def logout(
    token: TokenDep,
    token_repo: TokenRepositoryDep,
):
    await token_repo.deactivate_token(token.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserDep):
    return current_user
