from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from src.schemas.user import UserBrief
from src.schemas.tag import TagOut

class PostCreate(BaseModel):
    body: str = Field(
        ...,  # required
        min_length=1,
        max_length=500,
        description="Post content (1-500 characters)"
    )
    parent_id: Optional[int] = Field(
        None,
        description="ID of post being replied to (for threads)"
    )
    repost_of_id: Optional[int] = Field(
        None,
        description="ID of post being reposted/quoted"
    )
    
    @field_validator("body")
    @classmethod
    def body_not_empty(cls, v: str) -> str:
        """Ensure body isn't just whitespace."""
        if not v.strip():
            raise ValueError("Post body cannot be empty or whitespace only")
        return v


class PostUpdate(BaseModel):
    body: Optional[str] = Field(None, min_length=1, max_length=500)
    
    @field_validator("body")
    @classmethod
    def body_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Post body cannot be empty or whitespace only")
        return v

class PostOut(BaseModel):

    id: int
    body: str
    
    # Nested objects
    author: UserBrief
    tags: list[TagOut] = []
    
    # Engagement counts (computed in service layer)
    like_count: int = 0
    reply_count: int = 0
    repost_count: int = 0
    
    # User-specific state (set based on requesting user)
    is_liked: bool = False  # Did the current user like this?
    
    # Thread info
    parent_id: Optional[int] = None
    repost_of_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allow creating from ORM objects


class PostBrief(BaseModel):
    """
    Minimal post info for nested responses.
    
    Used when posts appear inside other objects (e.g., in repost references).
    """
    id: int
    body: str
    author: UserBrief
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostWithReplies(PostOut):
    """
    Post with its replies included.
    
    Used for thread views.
    """
    replies: list["PostOut"] = []


class PostList(BaseModel):
    """
    Paginated list of posts.
    
    Includes metadata for pagination UI.
    """
    items: list[PostOut]
    total: int
    limit: int
    offset: int
    has_more: bool


class LikeResponse(BaseModel):
    """Response after liking/unliking a post."""
    liked: bool  # True if now liked, False if unliked
    like_count: int  # Updated count