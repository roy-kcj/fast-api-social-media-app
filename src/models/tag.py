from tortoise import Model, fields


class Tag(Model):
    id = fields.IntField(pk=True)
    
    name = fields.CharField(
        max_length=50,
        unique=True,
    )
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "tags"
        ordering = ["name"]