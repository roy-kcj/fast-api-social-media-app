import asyncio
from src.services.views import view_service

async def flush_views_job():
    """Background job to flush views to DB every 5 minutes"""
    while True:
        try:
            count = await view_service.flush_to_db()
            if count > 0:
                print(f"Flushed {count} views to database")
        except Exception as e:
            print(f"Error flushing views: {e}")
        
        await asyncio.sleep(300)  # 5 minutes