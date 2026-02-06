# backend/src/services/views.py
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from src.core.redis import get_redis
from src.models.user import User
from src.models.post import Post

# Redis key patterns
def user_views_key(user_id: int) -> str:
    """Redis key for user's viewed posts"""
    return f"user:{user_id}:viewed_posts"

def pending_views_key() -> str:
    """Redis key for views pending DB flush"""
    return "pending_views"


class ViewService:
    # How long to keep views in Redis (7 days)
    VIEW_EXPIRY_SECONDS = 7 * 24 * 60 * 60
    
    async def mark_viewed(self, user_id: int, post_ids: list[int]) -> None:
        """
        Mark posts as viewed by user.
        Stores in Redis for fast read, queues for DB write.
        """
        if not post_ids:
            return
            
        redis = await get_redis()
        pipe = redis.pipeline()
        
        user_key = user_views_key(user_id)
        timestamp = datetime.utcnow().timestamp()
        
        for post_id in post_ids:
            # Add to user's viewed set (for filtering feed)
            pipe.sadd(user_key, post_id)
            
            # Queue for DB flush: "user_id:post_id:timestamp"
            pipe.sadd(pending_views_key(), f"{user_id}:{post_id}:{timestamp}")
        
        # Set/refresh expiry on user's viewed set
        pipe.expire(user_key, self.VIEW_EXPIRY_SECONDS)
        
        await pipe.execute()
    
    async def has_viewed(self, user_id: int, post_id: int) -> bool:
        """Check if user has viewed a post (Redis only, fast)"""
        redis = await get_redis()
        return await redis.sismember(user_views_key(user_id), post_id)
    
    async def get_viewed_posts(self, user_id: int) -> set[int]:
        """Get all post IDs viewed by user from Redis"""
        redis = await get_redis()
        viewed = await redis.smembers(user_views_key(user_id))
        return {int(post_id) for post_id in viewed}
    
    async def filter_unviewed(self, user_id: int, post_ids: list[int]) -> list[int]:
        """Filter list to only unviewed posts"""
        if not post_ids:
            return []
        
        viewed = await self.get_viewed_posts(user_id)
        return [pid for pid in post_ids if pid not in viewed]
    
    async def flush_to_db(self) -> int:
        """
        Flush pending views from Redis to PostgreSQL.
        Called by background job every 5 minutes.
        Returns number of views flushed.
        """
        redis = await get_redis()
        
        # Get all pending views
        pending = await redis.smembers(pending_views_key())
        if not pending:
            return 0
        
        # Parse and batch insert
        from src.models.post_view import PostView  # Import here to avoid circular
        
        views_to_create = []
        for item in pending:
            try:
                user_id, post_id, timestamp = item.split(":")
                views_to_create.append(
                    PostView(
                        user_id=int(user_id),
                        post_id=int(post_id),
                        viewed_at=datetime.fromtimestamp(float(timestamp)),
                    )
                )
            except (ValueError, TypeError):
                continue
        
        if views_to_create:
            # Bulk insert, ignore duplicates
            await PostView.bulk_create(
                views_to_create,
                ignore_conflicts=True,
            )
        
        # Clear pending set
        await redis.delete(pending_views_key())
        
        return len(views_to_create)


view_service = ViewService()