from tortoise.models import Model
from tortoise import fields

class AllowedChannels(Model):
    bot_config = fields.ForeignKeyField('models.BotConfig', related_name='allowed_channels', pk=True)
    channel_id = fields.BigIntField()
    
    class Meta:
        table = 'allowed_channels'