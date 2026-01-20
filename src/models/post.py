from tortoise import Model, fields


class Post(Model):
    
    id = fields.IntField(pk=True)
    
    body = fields.TextField(
        max_length=500,  # Like Twitter's extended tweets
        description="Post content (max 500 chars)"
    )
    
    author = fields.ForeignKeyField(
        "models.User",
        related_name="posts",  # user.posts returns all posts by user
        on_delete=fields.CASCADE,  # Delete posts when user is deleted
        description="Post author"
    )
    
    tags = fields.ManyToManyField(
        "models.Tag",
        related_name="posts",  # tag.posts returns all posts with this tag
        through="post_tags",   # Junction table name
        description="Hashtags in this post"
    )
    
    liked_by = fields.ManyToManyField(
        "models.User",
        related_name="liked_posts",  # user.liked_posts returns posts user liked
        through="post_likes",        # Junction table name
        description="Users who liked this post"
    )
    
    # Reply/Thread Support (for future implementation)
    # Self-referential: This post is a reply to another post
    parent = fields.ForeignKeyField(
        "models.Post",
        related_name="replies",  # post.replies returns all replies to this post
        on_delete=fields.SET_NULL,  # Keep replies if parent deleted
        null=True,
        description="Parent post if this is a reply"
    )
    
    repost_of = fields.ForeignKeyField(
        "models.Post",
        related_name="reposts",
        on_delete=fields.SET_NULL,
        null=True,
        description="Original post if this is a repost"
    )
    
    is_deleted = fields.BooleanField(
        default=False,
        description="Soft delete flag"
    )
    
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Post creation time"
    )
    
    updated_at = fields.DatetimeField(
        auto_now=True,
        description="Last edit time"
    )
    
    class Meta:
        table = "posts"
        ordering = ["-created_at"]  # Newest first
    
    def __str__(self) -> str:
        preview = self.body[:30] + "..." if len(self.body) > 30 else self.body
        return f"Post(id={self.id}, author_id={self.author_id}, body='{preview}')"
    
    class PydanticMeta:
        # Like_count, reply_count in the service layer
        pass


class Media(Model):
    
    id = fields.IntField(pk=True)
    
    post = fields.ForeignKeyField(
        "models.Post",
        related_name="media",  # post.media returns all media for post
        on_delete=fields.CASCADE,
        description="Parent post"
    )
    
    # Media details
    url = fields.CharField(
        max_length=500,
        description="URL to media file (S3, CDN, etc.)"
    )
    
    media_type = fields.CharField(
        max_length=20,
        description="Type: image, video, gif"
    )
    
    width = fields.IntField(null=True)
    height = fields.IntField(null=True)
    alt_text = fields.CharField(max_length=500, null=True, description="Accessibility text")
    
    position = fields.IntField(default=0, description="Order in post's media gallery")
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "post_media"
        ordering = ["position"]