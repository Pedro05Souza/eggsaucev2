from tortoise.models import Model
from tortoise import fields

__all__ = ['RankedPlayer']

class RankedPlayer(Model):
    player = fields.OneToOneField('models.Player', pk=True, related_name='ranked_player')
    current_mmr = fields.IntField(default=0)
    highest_mmr = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    
    class Meta:
        table = 'ranked_player'