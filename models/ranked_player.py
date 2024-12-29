from tortoise.models import Model
from tortoise import fields

__all__ = ['RankedPlayer']

class RankedPlayer(Model):
    player = fields.OneToOneField('models.Player', pk=True, related_name='ranked_player')
    current_mmr = fields.IntField()
    highest_mmr = fields.IntField()
    wins = fields.IntField()
    losses = fields.IntField()
    
    class Meta:
        table = 'ranked_player'