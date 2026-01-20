from fastapi import APIRouter, Query
from src.models.tag import Tag
from src.schemas.tag import TagOut
from src.services.tags import get_trending_tags

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/trending", response_model=list[TagOut])
async def trending_tags(limit: int = Query(10, le=50)):
    return await get_trending_tags(limit)

@router.get("/", response_model=list[TagOut])
async def list_tags():
    return await Tag.all()