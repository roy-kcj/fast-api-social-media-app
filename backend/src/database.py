from tortoise.contrib.fastapi import register_tortoise
from src.core.config import get_settings

settings = get_settings()


def init_db(app):
    """
    Initialize database connection with FastAPI app.
    
    This function:
    1. Connects to the database specified in DATABASE_URL
    2. Auto-creates tables if they don't exist (dev only)
    3. Registers shutdown handlers to close connections
    
    Args:
        app: FastAPI application instance
    """
    register_tortoise(
        app,
        db_url=settings.database_url,
        modules={"models": ["src.models"]},
        generate_schemas=True,  # Auto-create tables (disable in production with migrations)
        add_exception_handlers=True,
    )


# Tortoise ORM config for Aerich migrations (for later)
# Use for proper database migrations instead of auto-create
#
# Setup:
#   pip install aerich
#   aerich init -t src.database.TORTOISE_ORM
#   aerich init-db
#
# After model changes:
#   aerich migrate --name "description_of_change"
#   aerich upgrade

TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url,
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}