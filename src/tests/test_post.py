import pytest
from httpx import AsyncClient

from src.models.user import User
from src.models.post import Post
from src.models.tag import Tag
from src.core.security import hash_password, create_access_token


class TestCreatePost:
    """Tests for POST /posts endpoint."""
    
    @pytest.mark.anyio
    async def test_create_post_success(self, client: AsyncClient, auth_headers):
        """Test creating a post with valid data."""
        payload = {"body": "Hello world! This is my first post."}
        
        response = await client.post("/posts/", json=payload, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "Hello world! This is my first post."
        assert data["author"]["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.anyio
    async def test_create_post_with_hashtags(self, client: AsyncClient, auth_headers):
        """Test that hashtags are automatically extracted."""
        payload = {"body": "Learning #Python and #FastAPI today!"}
        
        response = await client.post("/posts/", json=payload, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "python" in tag_names
        assert "fastapi" in tag_names
    
    @pytest.mark.anyio
    async def test_create_post_requires_auth(self, client: AsyncClient, init_db):
        """Test that creating a post requires authentication."""
        payload = {"body": "This should fail"}
        
        response = await client.post("/posts/", json=payload)
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_create_post_empty_body_fails(self, client: AsyncClient, auth_headers):
        """Test that empty body is rejected."""
        payload = {"body": ""}
        
        response = await client.post("/posts/", json=payload, headers=auth_headers)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_create_post_whitespace_body_fails(self, client: AsyncClient, auth_headers):
        """Test that whitespace-only body is rejected."""
        payload = {"body": "   \n\t  "}
        
        response = await client.post("/posts/", json=payload, headers=auth_headers)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_create_post_too_long_fails(self, client: AsyncClient, auth_headers):
        """Test that body over 500 chars is rejected."""
        payload = {"body": "x" * 501}
        
        response = await client.post("/posts/", json=payload, headers=auth_headers)
        
        assert response.status_code == 422


class TestReadPosts:
    """Tests for GET /posts endpoints."""
    
    @pytest.mark.anyio
    async def test_list_posts_empty(self, client: AsyncClient, init_db):
        """Test listing posts when none exist."""
        response = await client.get("/posts/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
    
    @pytest.mark.anyio
    async def test_list_posts(self, client: AsyncClient, sample_post):
        """Test listing posts returns posts."""
        response = await client.get("/posts/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["body"] == sample_post.body
    
    @pytest.mark.anyio
    async def test_list_posts_pagination(self, client: AsyncClient, multiple_posts):
        """Test pagination works correctly."""
        response = await client.get("/posts/?limit=3&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 8
        assert data["has_more"] is True
        
        # Get second page
        response = await client.get("/posts/?limit=3&offset=3")
        data = response.json()
        assert len(data["items"]) == 3
        assert data["has_more"] is True
    
    @pytest.mark.anyio
    async def test_list_posts_filter_by_author(
        self, client: AsyncClient, multiple_posts, other_user
    ):
        """Test filtering posts by author."""
        response = await client.get(f"/posts/?author_id={other_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        
        for post in data["items"]:
            assert post["author"]["username"] == "otheruser"
    
    @pytest.mark.anyio
    async def test_list_posts_filter_by_tag(self, client: AsyncClient, sample_post):
        """Test filtering posts by tag."""
        response = await client.get("/posts/?tag=python")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "python" in [t["name"] for t in data["items"][0]["tags"]]
    
    @pytest.mark.anyio
    async def test_get_single_post(self, client: AsyncClient, sample_post):
        """Test getting a single post by ID."""
        response = await client.get(f"/posts/{sample_post.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_post.id
        assert data["body"] == sample_post.body
    
    @pytest.mark.anyio
    async def test_get_nonexistent_post(self, client: AsyncClient, init_db):
        """Test getting a post that doesn't exist."""
        response = await client.get("/posts/99999")
        
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_list_posts_shows_is_liked_when_authenticated(
        self, client: AsyncClient, sample_post, test_user, auth_headers
    ):
        """Test that is_liked field works when authenticated."""
        await sample_post.liked_by.add(test_user)
        
        response = await client.get("/posts/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["is_liked"] is True
    
    @pytest.mark.anyio
    async def test_list_posts_is_liked_false_when_anonymous(
        self, client: AsyncClient, sample_post
    ):
        """Test that is_liked is false for anonymous users."""
        response = await client.get("/posts/")
        
        data = response.json()
        assert data["items"][0]["is_liked"] is False


class TestUpdatePost:
    """Tests for PATCH /posts/{id} endpoint."""
    
    @pytest.mark.anyio
    async def test_update_own_post(self, client: AsyncClient, sample_post, auth_headers):
        """Test updating your own post."""
        payload = {"body": "Updated content #newhashtag"}
        
        response = await client.patch(
            f"/posts/{sample_post.id}",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["body"] == "Updated content #newhashtag"
        
        tag_names = [t["name"] for t in data["tags"]]
        assert "newhashtag" in tag_names
    
    @pytest.mark.anyio
    async def test_update_other_users_post_fails(
        self, client: AsyncClient, sample_post, other_user_headers
    ):
        """Test that you cannot update someone else's post."""
        payload = {"body": "Trying to hack!"}
        
        response = await client.patch(
            f"/posts/{sample_post.id}",
            json=payload,
            headers=other_user_headers
        )
        
        assert response.status_code == 403
        assert "own" in response.json()["detail"].lower()
    
    @pytest.mark.anyio
    async def test_update_post_requires_auth(self, client: AsyncClient, sample_post):
        """Test that updating requires authentication."""
        payload = {"body": "Anonymous update attempt"}
        
        response = await client.patch(f"/posts/{sample_post.id}", json=payload)
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_update_nonexistent_post(self, client: AsyncClient, auth_headers):
        """Test updating a post that doesn't exist."""
        payload = {"body": "Updating nothing"}
        
        response = await client.patch(
            "/posts/99999",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestDeletePost:
    """Tests for DELETE /posts/{id} endpoint."""
    
    @pytest.mark.anyio
    async def test_delete_own_post(self, client: AsyncClient, sample_post, auth_headers):
        """Test deleting your own post."""
        response = await client.delete(
            f"/posts/{sample_post.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        get_response = await client.get(f"/posts/{sample_post.id}")
        assert get_response.status_code == 404
    
    @pytest.mark.anyio
    async def test_delete_other_users_post_fails(
        self, client: AsyncClient, sample_post, other_user_headers
    ):
        """Test that you cannot delete someone else's post."""
        response = await client.delete(
            f"/posts/{sample_post.id}",
            headers=other_user_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.anyio
    async def test_delete_post_requires_auth(self, client: AsyncClient, sample_post):
        """Test that deleting requires authentication."""
        response = await client.delete(f"/posts/{sample_post.id}")
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_delete_nonexistent_post(self, client: AsyncClient, auth_headers):
        """Test deleting a post that doesn't exist."""
        response = await client.delete("/posts/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_admin_can_delete_any_post(
        self, client: AsyncClient, sample_post, admin_headers
    ):
        """Test that admins can delete any post."""
        response = await client.delete(
            f"/posts/{sample_post.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 204


class TestLikePosts:
    """Tests for post like/unlike functionality."""
    
    @pytest.mark.anyio
    async def test_like_post(self, client: AsyncClient, sample_post, auth_headers):
        """Test liking a post."""
        response = await client.post(
            f"/posts/{sample_post.id}/like",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["liked"] is True
        assert data["like_count"] == 1
    
    @pytest.mark.anyio
    async def test_like_post_idempotent(self, client: AsyncClient, sample_post, auth_headers):
        """Test that liking twice doesn't double count."""
        await client.post(f"/posts/{sample_post.id}/like", headers=auth_headers)
        
        response = await client.post(
            f"/posts/{sample_post.id}/like",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["like_count"] == 1
    
    @pytest.mark.anyio
    async def test_unlike_post(self, client: AsyncClient, sample_post, auth_headers):
        """Test unliking a post."""
        await client.post(f"/posts/{sample_post.id}/like", headers=auth_headers)
        
        response = await client.delete(
            f"/posts/{sample_post.id}/like",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["liked"] is False
        assert data["like_count"] == 0
    
    @pytest.mark.anyio
    async def test_toggle_like(self, client: AsyncClient, sample_post, auth_headers):
        """Test toggle like endpoint."""
        response = await client.post(
            f"/posts/{sample_post.id}/like/toggle",
            headers=auth_headers
        )
        assert response.json()["liked"] is True
        
        response = await client.post(
            f"/posts/{sample_post.id}/like/toggle",
            headers=auth_headers
        )
        assert response.json()["liked"] is False
    
    @pytest.mark.anyio
    async def test_like_requires_auth(self, client: AsyncClient, sample_post):
        """Test that liking requires authentication."""
        response = await client.post(f"/posts/{sample_post.id}/like")
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_like_nonexistent_post(self, client: AsyncClient, auth_headers):
        """Test liking a post that doesn't exist."""
        response = await client.post("/posts/99999/like", headers=auth_headers)
        
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_multiple_users_can_like(
        self, client: AsyncClient, sample_post, auth_headers, other_user_headers
    ):
        """Test that multiple users can like the same post."""
        await client.post(f"/posts/{sample_post.id}/like", headers=auth_headers)
        
        response = await client.post(
            f"/posts/{sample_post.id}/like",
            headers=other_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["like_count"] == 2


class TestFeed:
    """Tests for GET /posts/feed endpoint."""
    
    @pytest.mark.anyio
    async def test_feed_requires_auth(self, client: AsyncClient, init_db):
        """Test that feed requires authentication."""
        response = await client.get("/posts/feed")
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_feed_shows_own_posts(
        self, client: AsyncClient, sample_post, auth_headers
    ):
        """Test that feed includes your own posts."""
        response = await client.get("/posts/feed", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        post_ids = [p["id"] for p in data["items"]]
        assert sample_post.id in post_ids
    
    @pytest.mark.anyio
    async def test_feed_shows_followed_users_posts(
        self, client: AsyncClient, test_user, other_user, auth_headers
    ):
        """Test that feed includes posts from followed users."""
        other_post = await Post.create(
            body="Post by someone I follow",
            author=other_user,
        )
        
        await test_user.following.add(other_user)
        
        response = await client.get("/posts/feed", headers=auth_headers)
        
        data = response.json()
        post_ids = [p["id"] for p in data["items"]]
        assert other_post.id in post_ids
    
    @pytest.mark.anyio
    async def test_feed_excludes_unfollowed_users(
        self, client: AsyncClient, test_user, other_user, auth_headers
    ):
        """Test that feed excludes posts from non-followed users."""
        other_post = await Post.create(
            body="Post by someone I don't follow",
            author=other_user,
        )
        
        response = await client.get("/posts/feed", headers=auth_headers)
        
        data = response.json()
        post_ids = [p["id"] for p in data["items"]]
        assert other_post.id not in post_ids


class TestPostEdgeCases:
    """Edge case and security tests."""
    
    @pytest.mark.anyio
    async def test_deleted_post_not_in_list(
        self, client: AsyncClient, sample_post, auth_headers
    ):
        """Test that soft-deleted posts don't appear in lists."""
        await client.delete(f"/posts/{sample_post.id}", headers=auth_headers)
        
        response = await client.get("/posts/")
        data = response.json()
        
        post_ids = [p["id"] for p in data["items"]]
        assert sample_post.id not in post_ids
    
    @pytest.mark.anyio
    async def test_hashtag_case_insensitive(self, client: AsyncClient, auth_headers):
        """Test that hashtags are case-insensitive."""
        payload = {"body": "Testing #PYTHON"}
        await client.post("/posts/", json=payload, headers=auth_headers)
        
        response = await client.get("/posts/?tag=python")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    @pytest.mark.anyio
    async def test_special_characters_in_body(self, client: AsyncClient, auth_headers):
        """Test that special characters are handled correctly."""
        payload = {"body": "Test with émojis 🎉 and spëcial chars"}
        
        response = await client.post("/posts/", json=payload, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "🎉" in data["body"]