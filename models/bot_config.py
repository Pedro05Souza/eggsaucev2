from tortoise.models import Model
from tortoise import fields


class BotConfig(Model):
    id = fields.UUIDField(pk=True)
    guild_id = fields.BigIntField()
    toggled_modules = fields.CharField(max_length=5)
    prefix = fields.CharField(max_length=5)

    class Meta:
        table = "bot_config"
