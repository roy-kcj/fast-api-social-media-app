from typing import Optional
from fastapi import HTTPException, status
from tortoise.exceptions import IntegrityError

from src.models.user import User
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

from src.core.config import get_settings
from src.schemas.auth import RegisterRequest

settings = get_settings()


class AuthService:
    """
    Authentication service handling user registration and login.
    
    Usage:
        auth_service = AuthService()
        user = await auth_service.register(data)
        tokens = await auth_service.login(email, password)
    """
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password
        
        Returns:
            User object if credentials valid, None otherwise
        """
        user = await User.get_or_none(email=email.lower())
        
        if user is None:
            # Still hash to prevent timing attacks
            # (response time would differ if we skip hashing for non-existent users)
            hash_password("dummy_password_for_timing")
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def register(self, data: RegisterRequest) -> User:
        """
        Register a new user.
        
        Args:
            data: Registration data (username, email, password)
        
        Returns:
            Created User object
        
        Raises:
            HTTPException 409: If username or email already exists
        """
        # Check for existing username
        existing_username = await User.get_or_none(username=data.username.lower())
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )
        
        # Check for existing email
        existing_email = await User.get_or_none(email=data.email.lower())
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        try:
            user = await User.create(
                username=data.username.lower(),
                email=data.email.lower(),
                password_hash=hash_password(data.password),
            )
            return user
        except IntegrityError:
            # Race condition - another request created the user
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already registered"
            )
    
    def create_tokens(self, user: User) -> dict:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: User object
        
        Returns:
            Dict with access_token, refresh_token, token_type, expires_in
        """
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,  # Convert to seconds
        }
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Dict with new access_token, token_type, expires_in
        
        Raises:
            HTTPException 401: If refresh token is invalid
        """
        payload = decode_token(refresh_token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await User.get_or_none(id=int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        access_token = create_access_token(user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }


auth_service = AuthService()