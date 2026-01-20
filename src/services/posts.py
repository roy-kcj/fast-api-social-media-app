from typing import Optional
from fastapi import HTTPException, status
from tortoise.expressions import Q
from tortoise.functions import Count

from src.models.post import Post
from src.models.user import User
from src.models.tag import Tag
from src.schemas.post import PostCreate, PostUpdate, PostOut, PostList
from src.schemas.user import UserBrief
from src.schemas.tag import TagOut
from src.services.tags import extract_tag_names, get_or_create_tags


class PostService:
    
    async def create_post(
        self,
        data: PostCreate,
        author: User
    ) -> Post:
        
        # Validate parent post if this is a reply
        if data.parent_id:
            parent = await Post.get_or_none(id=data.parent_id, is_deleted=False)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent post not found"
                )
        
        # Validate repost if this is a repost/quote
        if data.repost_of_id:
            original = await Post.get_or_none(id=data.repost_of_id, is_deleted=False)
            if not original:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Original post not found"
                )
        
        # Create the post
        post = await Post.create(
            body=data.body,
            author=author,
            parent_id=data.parent_id,
            repost_of_id=data.repost_of_id,
        )
        
        # Extract and link tags
        tag_names = extract_tag_names(data.body)
        if tag_names:
            tags = await get_or_create_tags(tag_names)
            await post.tags.add(*tags)
        
        # Reload with relationships for response
        await post.fetch_related("author", "tags", "liked_by")
        
        return post
    
    async def get_post(
        self,
        post_id: int,
        current_user: Optional[User] = None
    ) -> PostOut:
        """
        Get a single post by ID.
        
        Args:
            post_id: Post ID to fetch
            current_user: Optional authenticated user (for is_liked status)
        
        Returns:
            PostOut schema with all details
        """
        post = await Post.get_or_none(
            id=post_id,
            is_deleted=False
        ).prefetch_related("author", "tags", "liked_by", "replies")
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return await self._post_to_schema(post, current_user)
    
    async def list_posts(
        self,
        limit: int = 20,
        offset: int = 0,
        author_id: Optional[int] = None,
        tags: Optional[list[str]] = None,
        current_user: Optional[User] = None,
    ) -> PostList:
        """
        List posts with filtering and pagination.
        
        Args:
            limit: Max posts to return
            offset: Number of posts to skip
            author_id: Filter by author
            tag: Filter by tag name
            current_user: For is_liked status
        
        Returns:
            PostList with items and pagination info
        """
        query = Post.filter(is_deleted=False)
        
        if author_id:
            query = query.filter(author_id=author_id)
        
        if tags:
            query = query.filter(tags__name_in=[t.lower() for t in tags])
        
        # Get total count for pagination
        total = await query.count()
        
        # Fetch posts with relationships
        posts = await query.prefetch_related(
            "author", "tags", "liked_by"
        ).order_by("-created_at").offset(offset).limit(limit)
        
        # Convert to schemas
        items = [
            await self._post_to_schema(post, current_user)
            for post in posts
        ]
        
        return PostList(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        )
    
    async def get_feed(
        self,
        user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> PostList:
        """
        Get personalized feed for a user.
        
        Shows posts from:
        - Users they follow
        - Their own posts
        
        This is a simple chronological feed. For production,
        you'd want algorithmic ranking, Redis caching, etc.
        """
        # Get IDs of users being followed
        following_ids = await user.following.all().values_list("id", flat=True)
        following_ids = list(following_ids) + [user.id]  # Include own posts
        
        query = Post.filter(
            is_deleted=False,
            author_id__in=following_ids
        )
        
        total = await query.count()
        
        posts = await query.prefetch_related(
            "author", "tags", "liked_by"
        ).order_by("-created_at").offset(offset).limit(limit)
        
        items = [await self._post_to_schema(post, user) for post in posts]
        
        return PostList(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        )
    
    async def update_post(
        self,
        post_id: int,
        data: PostUpdate,
        current_user: User,
    ) -> PostOut:
        """
        Update a post.
        
        Only the author can update their own post.
        Re-extracts tags if body is changed.
        """
        post = await Post.get_or_none(id=post_id, is_deleted=False)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Ownership check
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own posts"
            )
        
        # Update fields that were provided
        update_data = data.model_dump(exclude_unset=True)
        
        if "body" in update_data:
            # Re-extract tags from new body
            old_tags = await post.tags.all()
            await post.tags.clear()
            
            new_tag_names = extract_tag_names(update_data["body"])
            if new_tag_names:
                new_tags = await get_or_create_tags(new_tag_names)
                await post.tags.add(*new_tags)
        
        # Apply updates
        for field, value in update_data.items():
            setattr(post, field, value)
        
        await post.save()
        await post.fetch_related("author", "tags", "liked_by")
        
        return await self._post_to_schema(post, current_user)
    
    async def delete_post(
        self,
        post_id: int,
        current_user: User,
    ) -> None:
        """
        Soft delete a post.
        
        Only the author (or admin) can delete.
        """
        post = await Post.get_or_none(id=post_id, is_deleted=False)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Ownership check (admins can also delete)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own posts"
            )
        
        # Soft delete
        post.is_deleted = True
        await post.save()
    
    async def like_post(
        self,
        post_id: int,
        user: User,
    ) -> dict:
        """
        Like a post.
        
        Returns current like status and count.
        """
        post = await Post.get_or_none(
            id=post_id, is_deleted=False
        ).prefetch_related("liked_by")
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if already liked
        already_liked = await post.liked_by.filter(id=user.id).exists()
        
        if not already_liked:
            await post.liked_by.add(user)
        
        like_count = await post.liked_by.all().count()
        
        return {
            "liked": True,
            "like_count": like_count
        }
    
    async def unlike_post(
        self,
        post_id: int,
        user: User,
    ) -> dict:
        """
        Remove like from a post.
        """
        post = await Post.get_or_none(
            id=post_id, is_deleted=False
        ).prefetch_related("liked_by")
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Remove like if exists
        await post.liked_by.remove(user)
        
        like_count = await post.liked_by.all().count()
        
        return {
            "liked": False,
            "like_count": like_count
        }
    
    async def toggle_like(
        self,
        post_id: int,
        user: User,
    ) -> dict:
        """
        Toggle like status on a post.
        
        More convenient for frontends - single endpoint handles both.
        """
        post = await Post.get_or_none(
            id=post_id, is_deleted=False
        ).prefetch_related("liked_by")
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check current status and toggle
        is_liked = await post.liked_by.filter(id=user.id).exists()
        
        if is_liked:
            await post.liked_by.remove(user)
        else:
            await post.liked_by.add(user)
        
        like_count = await post.liked_by.all().count()
        
        return {
            "liked": not is_liked,
            "like_count": like_count
        }
    
    
    async def _post_to_schema(
        self,
        post: Post,
        current_user: Optional[User] = None
    ) -> PostOut:
        """
        Convert Post ORM object to PostOut schema.
        
        Computes:
        - like_count
        - reply_count  
        - repost_count
        - is_liked (for current user)
        """
        # Get counts
        like_count = await post.liked_by.all().count()
        reply_count = await Post.filter(parent_id=post.id, is_deleted=False).count()
        repost_count = await Post.filter(repost_of_id=post.id, is_deleted=False).count()
        
        # Check if current user liked this post
        is_liked = False
        if current_user:
            is_liked = await post.liked_by.filter(id=current_user.id).exists()
        
        # Build author brief
        author = await post.author  # May already be prefetched
        author_brief = UserBrief(
            id=author.id,
            username=author.username,
            display_name=author.display_name,
            profile_image=author.profile_image,
            is_verified=author.is_verified,
        )
        
        # Build tags list
        tags = [TagOut(id=t.id, name=t.name) for t in post.tags]
        
        return PostOut(
            id=post.id,
            body=post.body,
            author=author_brief,
            tags=tags,
            like_count=like_count,
            reply_count=reply_count,
            repost_count=repost_count,
            is_liked=is_liked,
            parent_id=post.parent_id,
            repost_of_id=post.repost_of_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )


# Singleton instance
post_service = PostService()