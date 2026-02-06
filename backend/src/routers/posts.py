from typing import Literal, Optional
from fastapi import APIRouter, Query, status, Depends
from typing import Annotated
from src.services.views import view_service

from src.models.user import User
from src.schemas.post import (
    PostCreate,
    PostUpdate,
    PostOut,
    PostList,
    LikeResponse,
)
from src.services.posts import post_service
from src.core.dependencies import CurrentUser
from fastapi.security import OAuth2PasswordBearer
from src.core.security import decode_token

router = APIRouter(prefix="/posts", tags=["Posts"])


# This doesn't REQUIRE auth but uses it if present
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)]
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    Use this for routes that are public but show extra info when logged in.
    Example: Post list shows "is_liked" only when authenticated.
    """
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    return await User.get_or_none(id=int(user_id), is_active=True)


OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]


@router.post(
    "/",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    responses={
        201: {"description": "Post created successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Parent post not found (if replying)"},
    }
)
async def create_post(
    data: PostCreate,
    user: CurrentUser,  # Requires authentication
):
    post = await post_service.create_post(data, user)
    return await post_service.get_post(post.id, user)

@router.get(
    "/",
    response_model=PostList,
    summary="List posts",
)
async def list_posts(
    user: OptionalUser,
    tags: Optional[list[str]] = Query(None, description="Filter by tag name"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    sort_by: Literal["recent", "popular"] = Query("recent", description="Sort order"),
    limit: int = Query(20, ge=1, le=100, description="Max posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
):
    
    return await post_service.list_posts(
        limit=limit,
        offset=offset,
        author_id=author_id,
        tags=tags,
        current_user=user,
        sort_by=sort_by,
    )


@router.get(
    "/feed",
    response_model=PostList,
    summary="Get personalized feed",
)
async def get_feed(
    user: CurrentUser,  # Requires authentication
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await post_service.get_feed(user, limit, offset)


@router.get(
    "/{post_id}",
    response_model=PostOut,
    summary="Get a single post",
    responses={
        200: {"description": "Post found"},
        404: {"description": "Post not found"},
    }
)
async def get_post(
    post_id: int,
    user: OptionalUser,
):
    return await post_service.get_post(post_id, user)

@router.patch(
    "/{post_id}",
    response_model=PostOut,
    summary="Update a post",
    responses={
        200: {"description": "Post updated"},
        401: {"description": "Authentication required"},
        403: {"description": "Not your post"},
        404: {"description": "Post not found"},
    }
)
async def update_post(
    post_id: int,
    data: PostUpdate,
    user: CurrentUser,
):
    return await post_service.update_post(post_id, data, user)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a post",
    responses={
        204: {"description": "Post deleted"},
        401: {"description": "Authentication required"},
        403: {"description": "Not your post"},
        404: {"description": "Post not found"},
    }
)
async def delete_post(
    post_id: int,
    user: CurrentUser,
):
    await post_service.delete_post(post_id, user)


@router.post(
    "/{post_id}/like",
    response_model=LikeResponse,
    summary="Like a post",
)
async def like_post(
    post_id: int,
    user: CurrentUser,
):
    return await post_service.like_post(post_id, user)


@router.delete(
    "/{post_id}/like",
    response_model=LikeResponse,
    summary="Unlike a post",
)
async def unlike_post(
    post_id: int,
    user: CurrentUser,
):
    return await post_service.unlike_post(post_id, user)


@router.post(
    "/{post_id}/like/toggle",
    response_model=LikeResponse,
    summary="Toggle like on a post",
)
async def toggle_like(
    post_id: int,
    user: CurrentUser,
):
    return await post_service.toggle_like(post_id, user)


@router.get(
    "/user/{username}",
    response_model=PostList,
    summary="Get posts by username",
)
async def get_user_posts(
    username: str,
    user: OptionalUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    from src.models.user import User as UserModel
    
    author = await UserModel.get_or_none(username=username.lower())
    if not author:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return await post_service.list_posts(
        limit=limit,
        offset=offset,
        author_id=author.id,
        current_user=user,
    )

@router.post(
    "/views",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Track viewed posts",
)
async def track_views(
    post_ids: list[int],
    user: CurrentUser,
):
    """
    Mark posts as viewed by current user.
    Used for feed personalization.
    """
    await view_service.mark_viewed(user.id, post_ids)