from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends

from src.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    AccessTokenResponse,
    MessageResponse,
)
from src.schemas.user import UserOut, UserPrivate
from src.services.auth import auth_service
from src.core.dependencies import CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def user_to_public_response(user) -> dict:
    """Public profile - no email (for viewing other users)."""
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "profile_image": user.profile_image,
        "banner_image": user.banner_image,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "follower_count": 0,
        "following_count": 0,
        "post_count": 0,
        "is_following": False,
        "is_followed_by": False,
    }


async def user_to_private_response(user) -> dict:
    """Private profile - includes email (for your own profile)."""

    follower_count = await user.followers.all().count()
    following_count = await user.following.all().count()
    post_count = await user.posts.filter(is_deleted=False).count()

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "bio": user.bio,
        "profile_image": user.profile_image,
        "banner_image": user.banner_image,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "follower_count": follower_count,
        "following_count": following_count,
        "post_count": post_count,
        "is_following": False,
        "is_followed_by": False,
    }

@router.post(
    "/register",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(data: RegisterRequest):
    """Register a new user account."""
    user = await auth_service.register(data)
    return await user_to_private_response(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get tokens",
)
async def login(data: LoginRequest):
    """Authenticate with email and password to receive JWT tokens."""
    user = await auth_service.authenticate(data.email, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_service.create_tokens(user)


@router.post(
    "/login/form",
    response_model=TokenResponse,
    summary="Login with OAuth2 form (for Swagger UI)",
)
async def login_form(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """OAuth2 compatible login endpoint for Swagger UI."""
    user = await auth_service.authenticate(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
)
async def refresh_token(data: RefreshTokenRequest):
    """Get a new access token using a valid refresh token."""
    return await auth_service.refresh_access_token(data.refresh_token)


@router.get(
    "/me",
    response_model=UserPrivate,
    summary="Get current user profile",
)
async def get_current_user_profile(user: CurrentUser):
    """Get the profile of the currently authenticated user."""
    return await user_to_private_response(user) 

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (client-side)",
)
async def logout(user: CurrentUser):
    """Logout endpoint - confirms token was valid."""
    return MessageResponse(message="Successfully logged out")