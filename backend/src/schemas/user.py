from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBrief(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    profile_image: Optional[str] = None
    is_verified: bool = False
    
    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    banner_image: Optional[str] = None
    is_verified: bool
    created_at: datetime
    
    # Social stats (computed in service layer)
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    
    # Relationship to current user (set based on requesting user)
    is_following: bool = False  # Does current user follow this user?
    is_followed_by: bool = False  # Does this user follow current user?
    
    class Config:
        from_attributes = True


class UserPrivate(UserOut):
    email: EmailStr
    is_active: bool
    is_admin: bool
    updated_at: datetime

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    profile_image: Optional[str] = Field(None, max_length=500)
    banner_image: Optional[str] = Field(None, max_length=500)
    
    @field_validator("bio")
    @classmethod
    def bio_reasonable(cls, v: Optional[str]) -> Optional[str]:
        """Allow empty string to clear bio."""
        if v is not None:
            return v.strip()
        return v


class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=72)
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password meets requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class FollowResponse(BaseModel):
    """Response after following/unfollowing a user."""
    following: bool  # True if now following, False if unfollowed
    follower_count: int  # Updated count for target user


class FollowerList(BaseModel):
    """Paginated list of followers/following."""
    items: list[UserBrief]
    total: int
    limit: int
    offset: int
    has_more: bool