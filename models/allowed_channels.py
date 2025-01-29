from tortoise.models import Model
from tortoise import fields

__all__ = ["AllowedChannels"]

class AllowedChannels(Model):
    bot_config = fields.ForeignKeyField(
        "models.BotConfig", related_name="allowed_channels"
    )
    channel_id = fields.BigIntField()

    class Meta:
        table = "allowed_channels"
        unique_together = ("bot_config", "channel_id")
