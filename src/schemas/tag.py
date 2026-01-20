from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TagOut(BaseModel):
    """Basic tag response."""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class TagWithCount(BaseModel):
    """
    Tag with post count.
    
    Used for trending tags display.
    """
    id: int
    name: str
    post_count: int = 0
    
    class Config:
        from_attributes = True


class TrendingTag(BaseModel):
    """
    Trending tag with additional metadata.
    """
    id: int
    name: str
    post_count: int


class TagCreate(BaseModel):
    """
    Schema for manually creating a tag.
    """
    name: str = Field(
        min_length=1,
        max_length=50,
        description="Tag name (without # symbol)"
    )
    
    @field_validator("name")
    @classmethod
    def normalize_tag_name(cls, v: str) -> str:
        """Normalize tag name to lowercase, no #, alphanumeric only."""
        import re
        
        name = v.lower().strip().lstrip("#")
        
        if not re.match(r"^[a-z0-9_]+$", name):
            raise ValueError("Tag name can only contain letters, numbers, and underscores")
        
        return name