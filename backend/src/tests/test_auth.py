import pytest
from httpx import AsyncClient

from src.models.user import User
from src.core.security import verify_password


class TestRegistration:
    
    @pytest.mark.anyio
    async def test_register_success(self, client: AsyncClient):
        """
        Test successful user registration.
        
        @pytest.mark.anyio: Marks this as an async test
        client: Injected by pytest from conftest.py fixtures
        """
        # Arrange: Prepare test data
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123"
        }
        
        # Act: Make the request
        response = await client.post("/auth/register", json=payload)
        
        # Assert: Check the response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # Password should never be returned
        assert "password_hash" not in data
    
    @pytest.mark.anyio
    async def test_register_creates_user_in_database(self, client: AsyncClient, init_db):
        """Test that registration actually creates a user in the DB."""
        payload = {
            "username": "dbuser",
            "email": "dbuser@example.com",
            "password": "SecurePass123"
        }
        
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 201
        
        # Verify user exists in database
        user = await User.get_or_none(email="dbuser@example.com")
        assert user is not None, "User should exist in database"
        assert user.username == "dbuser"
        
        # Verify password was hashed (not stored plain)
        assert user.password_hash != "SecurePass123"
        assert verify_password("SecurePass123", user.password_hash)
    
    @pytest.mark.anyio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """
        Test registration with existing email fails.
        
        Note: test_user fixture creates a user before this test runs.
        """
        payload = {
            "username": "different",
            "email": "test@example.com",  # Same as test_user
            "password": "SecurePass123"
        }
        
        response = await client.post("/auth/register", json=payload)
        
        assert response.status_code == 409  # Conflict
        assert "email" in response.json()["detail"].lower()
    
    @pytest.mark.anyio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with existing username fails."""
        payload = {
            "username": "testuser",  # Same as test_user
            "email": "different@example.com",
            "password": "SecurePass123"
        }
        
        response = await client.post("/auth/register", json=payload)
        
        assert response.status_code == 409
        assert "username" in response.json()["detail"].lower()
    
    @pytest.mark.anyio
    async def test_register_invalid_email(self, client: AsyncClient, init_db):
        """Test registration with invalid email format."""
        payload = {
            "username": "validuser",
            "email": "not-an-email",  # Invalid
            "password": "SecurePass123"
        }
        
        response = await client.post("/auth/register", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.anyio
    async def test_register_weak_password(self, client: AsyncClient, init_db):
        """Test registration with password missing requirements."""
        # Missing uppercase
        response = await client.post("/auth/register", json={
            "username": "validuser",
            "email": "valid@example.com",
            "password": "nouppercase123"
        })
        assert response.status_code == 422
        
        # Missing digit
        response = await client.post("/auth/register", json={
            "username": "validuser",
            "email": "valid@example.com",
            "password": "NoDigitsHere"
        })
        assert response.status_code == 422
        
        # Too short
        response = await client.post("/auth/register", json={
            "username": "validuser",
            "email": "valid@example.com",
            "password": "Short1"
        })
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_register_username_validation(self, client: AsyncClient, init_db):
        """Test username format validation."""
        # Username too short
        response = await client.post("/auth/register", json={
            "username": "ab",  # Min 3 chars
            "email": "valid@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 422
        
        # Username with invalid characters
        response = await client.post("/auth/register", json={
            "username": "user@name",  # @ not allowed
            "email": "valid@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for the login endpoint."""
    
    @pytest.mark.anyio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login returns tokens."""
        response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123"
        })
        
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        
        # Tokens should be non-empty strings
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    @pytest.mark.anyio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password fails."""
        response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword123"
        })
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    @pytest.mark.anyio
    async def test_login_nonexistent_user(self, client: AsyncClient, init_db):
        """Test login with non-existent email fails."""
        response = await client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePassword123"
        })
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_login_inactive_user(self, client: AsyncClient, init_db):
        """Test login with deactivated account fails."""
        # Create inactive user directly
        from src.core.security import hash_password
        await User.create(
            username="inactive",
            email="inactive@example.com",
            password_hash=hash_password("TestPassword123"),
            is_active=False,  # Deactivated
        )
        
        response = await client.post("/auth/login", json={
            "email": "inactive@example.com",
            "password": "TestPassword123"
        })
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_login_case_insensitive_email(self, client: AsyncClient, test_user):
        """Test that email matching is case-insensitive."""
        response = await client.post("/auth/login", json={
            "email": "TEST@EXAMPLE.COM",  # Uppercase
            "password": "TestPassword123"
        })
        
        # This may fail if your auth service doesn't lowercase emails
        # If it fails, update auth_service.authenticate to use email.lower()
        assert response.status_code == 200


class TestTokenRefresh:
    """Tests for token refresh endpoint."""
    
    @pytest.mark.anyio
    async def test_refresh_token_success(self, client: AsyncClient, test_user):
        """Test refreshing access token with valid refresh token."""
        # First, login to get tokens
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123"
        })
        tokens = login_response.json()
        
        # Now refresh
        response = await client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.anyio
    async def test_refresh_with_access_token_fails(self, client: AsyncClient, test_user):
        """Test that using access token for refresh fails."""
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123"
        })
        tokens = login_response.json()
        
        # Try to use access token as refresh token (should fail)
        response = await client.post("/auth/refresh", json={
            "refresh_token": tokens["access_token"]  # Wrong token type!
        })
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_refresh_with_invalid_token(self, client: AsyncClient, init_db):
        """Test refresh with garbage token fails."""
        response = await client.post("/auth/refresh", json={
            "refresh_token": "not.a.valid.token"
        })
        
        assert response.status_code == 401


class TestProtectedRoutes:
    """Tests for routes that require authentication."""
    
    @pytest.mark.anyio
    async def test_get_current_user_success(self, client: AsyncClient, test_user, auth_headers):
        """
        Test accessing protected route with valid token.
        
        auth_headers fixture provides: {"Authorization": "Bearer <token>"}
        """
        response = await client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password_hash" not in data
    
    @pytest.mark.anyio
    async def test_get_current_user_no_token(self, client: AsyncClient, init_db):
        """Test accessing protected route without token fails."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_get_current_user_invalid_token(self, client: AsyncClient, init_db):
        """Test accessing protected route with invalid token fails."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_get_current_user_malformed_header(self, client: AsyncClient, init_db):
        """Test various malformed authorization headers."""
        # Missing 'Bearer' prefix
        response = await client.get("/auth/me", headers={
            "Authorization": "some.token.here"
        })
        assert response.status_code == 401
        
        # Empty header
        response = await client.get("/auth/me", headers={
            "Authorization": ""
        })
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_get_current_user_expired_token(self, client: AsyncClient, test_user):
        """Test that expired tokens are rejected."""
        from datetime import timedelta
        from src.core.security import create_access_token
        
        # Create token that's already expired
        expired_token = create_access_token(
            test_user.id,
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401


class TestSecurityEdgeCases:
    """Security-focused tests."""
    
    @pytest.mark.anyio
    async def test_deleted_user_token_invalid(self, client: AsyncClient, init_db):
        """Test that tokens for deleted users don't work."""
        from src.core.security import hash_password, create_access_token
        
        # Create user
        user = await User.create(
            username="deleteme",
            email="delete@example.com",
            password_hash=hash_password("TestPassword123"),
        )
        user_id = user.id
        
        # Create token while user exists
        token = create_access_token(user_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify token works
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        # Delete user
        await user.delete()
        
        # Token should now be invalid
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_deactivated_user_token_invalid(self, client: AsyncClient, test_user, auth_headers):
        """Test that tokens for deactivated users don't work."""
        # Verify token works initially
        response = await client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        # Deactivate user
        test_user.is_active = False
        await test_user.save()
        
        # Token should now be invalid
        response = await client.get("/auth/me", headers=auth_headers)
        assert response.status_code in [401, 403]  # Either is acceptable
