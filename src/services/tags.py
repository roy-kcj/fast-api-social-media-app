import re
from typing import Set, List
from tortoise.functions import Count

from src.models.tag import Tag
from src.schemas.tag import TagWithCount

HASHTAG_REGEX = re.compile(r"#(\w+)", re.IGNORECASE)


def extract_tag_names(text: str) -> Set[str]:
    """
    Extract hashtag names from text.
    
    Args:
        text: Post body or any text content
    
    Returns:
        Set of lowercase tag names (without # symbol)
    
    Example:
        extract_tag_names("Learning #Python and #FastAPI!")
        # Returns: {"python", "fastapi"}
    """
    # findall returns list of captured groups (the part in parentheses)
    # So "#Python" returns "Python", not "#Python"
    matches = HASHTAG_REGEX.findall(text)
    
    # Normalize to lowercase and return as set (removes duplicates)
    return {match.lower() for match in matches}


async def get_or_create_tags(tag_names: Set[str]) -> List[Tag]:
    """
    Get existing tags or create new ones.
    
    Uses Tortoise's get_or_create for atomic operation.
    
    Args:
        tag_names: Set of tag names to get/create
    
    Returns:
        List of Tag objects
    """
    tags = []
    
    for name in tag_names:
        # get_or_create returns (object, created_bool)
        tag, created = await Tag.get_or_create(
            name=name,
            defaults={"name": name}  # Values to use if creating
        )
        tags.append(tag)
    
    return tags


async def get_trending_tags(limit: int = 10) -> List[TagWithCount]:
    """
    Get trending tags ordered by post count.
    
    "Trending" here means most-used tags.
    For real trending, you'd want time-windowed counts
    (e.g., posts in last 24 hours).
    
    Args:
        limit: Maximum number of tags to return
    
    Returns:
        List of tags with post counts
    """
    # Annotate adds a computed column to the query
    # Count("posts") counts the related posts for each tag
    tags = await Tag.annotate(
        post_count=Count("posts")
    ).order_by("-post_count").limit(limit)
    
    # Convert to schema
    return [
        TagWithCount(
            id=tag.id,
            name=tag.name,
            post_count=tag.post_count
        )
        for tag in tags
    ]


async def get_trending_tags_timewindow(
    hours: int = 24,
    limit: int = 10
) -> List[TagWithCount]:
    """
    Get trending tags within a time window.
    
    More realistic "trending" - counts recent posts only.
    
    Note: This is more complex and may need raw SQL for performance.
    For now, this is a simplified version.
    """
    from datetime import datetime, timedelta, timezone
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # This filters posts by created_at, then counts
    # In production, you might want a materialized view or cache
    tags = await Tag.annotate(
        post_count=Count("posts", _filter=Q(posts__created_at__gte=cutoff))
    ).filter(
        post_count__gt=0  # Only tags with recent posts
    ).order_by("-post_count").limit(limit)
    
    return [
        TagWithCount(
            id=tag.id,
            name=tag.name,
            post_count=tag.post_count
        )
        for tag in tags
    ]


async def search_tags(query: str, limit: int = 10) -> List[Tag]:
    """
    Search tags by name prefix.
    
    Used for autocomplete when user types #pyt...
    
    Args:
        query: Search prefix
        limit: Max results
    
    Returns:
        Matching tags
    """
    # Case-insensitive prefix search
    return await Tag.filter(
        name__istartswith=query.lower().lstrip("#")
    ).limit(limit)


# Import Q for complex queries (used in timewindow function)
from tortoise.expressions import Q