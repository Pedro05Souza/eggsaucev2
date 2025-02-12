from tortoise.models import Model
from tortoise import fields

__all__ = ["Cornfield"]


class Cornfield(Model):
    id = fields.UUIDField(pk=True)
    farm = fields.OneToOneField("models.Farm", related_name="cornfield")
    cornfield_title = fields.CharField(max_length=50)
    current_corn = fields.IntField(default=0)
    corn_limit = fields.IntField()
    plots = fields.IntField(default=1)
    next_corn_drop = fields.DatetimeField(null=True)
