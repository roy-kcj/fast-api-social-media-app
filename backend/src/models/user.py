from tortoise import Model, fields
from tortoise.validators import RegexValidator
import re


class User(Model):
    EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    
    id = fields.IntField(pk=True)
    
    username = fields.CharField(
        max_length=30,
        unique=True,
        description="Unique username"
    )
    
    email = fields.CharField(
        max_length=255,
        unique=True,
        validators=[RegexValidator(EMAIL_REGEX, flags=re.IGNORECASE)],
        description="User email address"
    )
    
    password_hash = fields.CharField(
        max_length=128,
        description="Bcrypt hashed password"
    )
    
    display_name = fields.CharField(
        max_length=50,
        null=True,
        description="Display name (can differ from username)"
    )
    
    bio = fields.TextField(
        null=True,
        default=None,
        description="User bio/description"
    )
    
    profile_image = fields.CharField(
        max_length=500,
        null=True,
        default=None,
        description="Profile image URL"
    )
    
    banner_image = fields.CharField(
        max_length=500,
        null=True,
        default=None,
        description="Profile banner image URL"
    )
    
    is_verified = fields.BooleanField(
        default=False,
        description="Email verification status"
    )
    
    is_active = fields.BooleanField(
        default=True,
        description="Account active status (soft delete)"
    )
    
    is_admin = fields.BooleanField(
        default=False,
        description="Admin privileges"
    )
    
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Account creation timestamp"
    )
    
    updated_at = fields.DatetimeField(
        auto_now=True,
        description="Last update timestamp"
    )
    
    following = fields.ManyToManyField(
        "models.User",
        related_name="followers",
        through="user_follows",
        description="Users this user follows"
    )
    
    class Meta:
        table = "users"
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        return f"User(id={self.id}, username={self.username})"
    
    class PydanticMeta:
        exclude = ["password_hash"]