from tortoise.models import Model
from tortoise import fields

__all__ = ['FarmCornfield']

class FarmCornfield(Model):
    id = fields.UUIDField(pk=True)
    farm = fields.OneToOneField('models.FarmPlayer', related_name='cornfield')
    cornfield_name = fields.CharField(max_length=50)
    current_corn = fields.IntField()
    corn_limit = fields.IntField()
    plot = fields.IntField()
    last_corn_drop = fields.DatetimeField(null=True)