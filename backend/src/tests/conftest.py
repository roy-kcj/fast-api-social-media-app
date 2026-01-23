import pytest
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise

from src.main import app
from src.models.user import User
from src.models.post import Post
from src.models.tag import Tag
from src.core.security import hash_password, create_access_token


# Database Fixtures
@pytest.fixture(scope="function")
async def init_db():
    """
    Initialize a fresh in-memory database for each test.
    
    Scope="function" means this runs for EACH test.
    """
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["src.models"]},
    )
    await Tortoise.generate_schemas()
    
    yield  # Test runs here
    
    await Tortoise.close_connections()


# HTTP Client Fixtures
@pytest.fixture(scope="function")
async def client(init_db):
    """
    Async HTTP client for testing endpoints.
    
    Depends on init_db, so database is ready before client is created.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# User Fixtures
@pytest.fixture
async def test_user(init_db) -> User:
    """Create a standard test user."""
    user = await User.create(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
async def other_user(init_db) -> User:
    """Create a second user for ownership/relationship testing."""
    user = await User.create(
        username="otheruser",
        email="other@example.com",
        password_hash=hash_password("TestPassword123"),
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
async def test_user_unverified(init_db) -> User:
    """Create an unverified test user."""
    user = await User.create(
        username="unverified",
        email="unverified@example.com",
        password_hash=hash_password("TestPassword123"),
        is_verified=False,
        is_active=True,
    )
    return user


@pytest.fixture
async def test_admin(init_db) -> User:
    """Create an admin test user."""
    user = await User.create(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123"),
        is_verified=True,
        is_active=True,
        is_admin=True,
    )
    return user


# Authentication Header Fixtures
@pytest.fixture
async def auth_headers(test_user) -> dict:
    """Authorization headers for test_user."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_user_headers(other_user) -> dict:
    """Authorization headers for other_user."""
    token = create_access_token(other_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(test_admin) -> dict:
    """Authorization headers for admin user."""
    token = create_access_token(test_admin.id)
    return {"Authorization": f"Bearer {token}"}


# Post Fixtures
@pytest.fixture
async def sample_post(test_user) -> Post:
    """Create a sample post with tags."""
    post = await Post.create(
        body="This is a test post #testing #python",
        author=test_user,
    )
    tag1, _ = await Tag.get_or_create(name="testing")
    tag2, _ = await Tag.get_or_create(name="python")
    await post.tags.add(tag1, tag2)
    return post


@pytest.fixture
async def multiple_posts(test_user, other_user) -> list[Post]:
    """Create multiple posts for pagination testing."""
    posts = []
    
    # 5 posts by test_user
    for i in range(5):
        post = await Post.create(
            body=f"Post number {i} by test_user",
            author=test_user,
        )
        posts.append(post)
    
    # 3 posts by other_user
    for i in range(3):
        post = await Post.create(
            body=f"Post number {i} by other_user",
            author=other_user,
        )
        posts.append(post)
    
    return posts


# Pytest Configuration
@pytest.fixture(scope="session")
def anyio_backend():
    """Tell pytest-asyncio to use asyncio backend."""
    return "asyncio"