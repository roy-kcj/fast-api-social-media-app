import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.redis import close_redis
from src.tasks.flush_views import flush_views_job
from src.database import init_db
from src.core.config import get_settings
from src.routers import auth, posts, tags, users

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    flush_task = asyncio.create_task(flush_views_job())
    
    yield
    
    # Shutdown
    flush_task.cancel()
    await close_redis()

app = FastAPI(
    title=settings.app_name,
    description="""
    A Twitter/Threads-style social media API.
    
    # Features
    
    - Authentication: JWT-based auth with access and refresh tokens
    - Posts: Create, read, update, delete posts with hashtag support
    - Tags: Automatic hashtag extraction and trending tags
    - Social: Follow users, like posts, personalized feed
    - Pagination: Cursor-based pagination for all list endpoints
    
    ## Authentication
    
    Most endpoints require authentication. Use the `/auth/login` endpoint to get tokens,
    then include the access token in the `Authorization` header:
    ```
    Authorization: Bearer <your-access-token>
    ```
    
    Use the "Authorize" button above to authenticate in this documentation.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS - Configure for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:5173",  # Vite dev server
        # Add production frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(tags.router)


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - useful for health checks.
    """
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}

init_db(app)