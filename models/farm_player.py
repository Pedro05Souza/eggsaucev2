from tortoise.models import Model
from tortoise import fields

__all__ = ['FarmPlayer']

class FarmPlayer(Model):
    id = fields.UUIDField(pk=True)
    player = fields.OneToOneField('models.Player', related_name='farm_player')
    farm_title = fields.CharField(max_length=50)
    farmer = fields.CharField(max_length=50)
    last_drop_time = fields.DatetimeField(auto_now=True)
    last_chicken_roll_time = fields.DatetimeField(auto_now=True)    
    
    class Meta:
        table = 'farm_player'