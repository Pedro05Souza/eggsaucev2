from tortoise.models import Model
from tortoise import fields


class BotConfig(Model):
    id = fields.UUIDField(pk=True)
    guild_id = fields.BigIntField()
    prefix = fields.CharField(max_length=5, default="$")
    can_steal_chickens = fields.BooleanField(default=False)

    class Meta:
        table = "bot_config"
