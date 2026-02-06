# backend/src/models/post_view.py
from tortoise import fields
from tortoise.models import Model

class PostView(Model):
    """Tracks which users have viewed which posts"""
    
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="post_views")
    post = fields.ForeignKeyField("models.Post", related_name="views")
    viewed_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "post_views"
        unique_together = (("user", "post"),)  # One view per user per post