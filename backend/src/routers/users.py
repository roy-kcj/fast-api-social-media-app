from fastapi import APIRouter, Query, status, HTTPException
from typing import Optional, Annotated
from fastapi import Depends

from src.models.user import User
from src.schemas.user import (
    UserOut,
    UserBrief,
    UserPrivate,
    UserUpdate,
    FollowResponse,
    FollowerList,
)
from src.core.dependencies import CurrentUser
from src.core.security import decode_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)]
) -> Optional[User]:
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


@router.get(
    "/me",
    response_model=UserPrivate,
    summary="Get your own profile",
)
async def get_my_profile(user: CurrentUser):
    """
    Get your own profile with private info (email, etc.)
    """
    return await _user_to_private_schema(user)


@router.patch(
    "/me",
    response_model=UserPrivate,
    summary="Update your profile",
)
async def update_my_profile(
    data: UserUpdate,
    user: CurrentUser,
):
    """
    Update your profile.
    
    Only provided fields are updated.
    """
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await user.save()
    return await _user_to_private_schema(user)


@router.get(
    "/{username}",
    response_model=UserOut,
    summary="Get user profile",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    }
)
async def get_user_profile(
    username: str,
    current_user: OptionalUser,
):
    """
    Get a user's public profile.
    
    If authenticated, includes follow relationship status.
    """
    user = await User.get_or_none(username=username.lower(), is_active=True)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return await _user_to_schema(user, current_user)


@router.post(
    "/{username}/follow",
    response_model=FollowResponse,
    summary="Follow a user",
)
async def follow_user(
    username: str,
    user: CurrentUser,
):
    """
    Follow a user.
    
    You cannot follow yourself.
    """
    target = await User.get_or_none(username=username.lower(), is_active=True)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if target.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    # Check if already following
    is_following = await user.following.filter(id=target.id).exists()
    
    if not is_following:
        await user.following.add(target)
    
    follower_count = await target.followers.all().count()
    
    return FollowResponse(
        following=True,
        follower_count=follower_count
    )


@router.delete(
    "/{username}/follow",
    response_model=FollowResponse,
    summary="Unfollow a user",
)
async def unfollow_user(
    username: str,
    user: CurrentUser,
):
    """
    Unfollow a user.
    """
    target = await User.get_or_none(username=username.lower(), is_active=True)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await user.following.remove(target)
    
    follower_count = await target.followers.all().count()
    
    return FollowResponse(
        following=False,
        follower_count=follower_count
    )


@router.get(
    "/{username}/followers",
    response_model=FollowerList,
    summary="Get user's followers",
)
async def get_followers(
    username: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get list of users who follow this user.
    """
    user = await User.get_or_none(username=username.lower(), is_active=True)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    total = await user.followers.all().count()
    followers = await user.followers.all().offset(offset).limit(limit)
    
    items = [
        UserBrief(
            id=f.id,
            username=f.username,
            display_name=f.display_name,
            profile_image=f.profile_image,
            is_verified=f.is_verified,
        )
        for f in followers
    ]
    
    return FollowerList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.get(
    "/{username}/following",
    response_model=FollowerList,
    summary="Get users this user follows",
)
async def get_following(
    username: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get list of users this user follows.
    """
    user = await User.get_or_none(username=username.lower(), is_active=True)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    total = await user.following.all().count()
    following = await user.following.all().offset(offset).limit(limit)
    
    items = [
        UserBrief(
            id=f.id,
            username=f.username,
            display_name=f.display_name,
            profile_image=f.profile_image,
            is_verified=f.is_verified,
        )
        for f in following
    ]
    
    return FollowerList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )

async def _user_to_schema(
    user: User,
    current_user: Optional[User] = None
) -> UserOut:
    """Convert User to UserOut schema with computed fields."""
    follower_count = await user.followers.all().count()
    following_count = await user.following.all().count()
    post_count = await user.posts.filter(is_deleted=False).count()
    
    # Check relationship with current user
    is_following = False
    is_followed_by = False
    
    if current_user and current_user.id != user.id:
        is_following = await current_user.following.filter(id=user.id).exists()
        is_followed_by = await user.following.filter(id=current_user.id).exists()
    
    return UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        profile_image=user.profile_image,
        banner_image=user.banner_image,
        is_verified=user.is_verified,
        created_at=user.created_at,
        follower_count=follower_count,
        following_count=following_count,
        post_count=post_count,
        is_following=is_following,
        is_followed_by=is_followed_by,
    )


async def _user_to_private_schema(user: User) -> UserPrivate:
    """Convert User to UserPrivate schema (includes email)."""
    follower_count = await user.followers.all().count()
    following_count = await user.following.all().count()
    post_count = await user.posts.filter(is_deleted=False).count()
    
    return UserPrivate(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        bio=user.bio,
        profile_image=user.profile_image,
        banner_image=user.banner_image,
        is_verified=user.is_verified,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at,
        follower_count=follower_count,
        following_count=following_count,
        post_count=post_count,
        is_following=False,
        is_followed_by=False,
    )