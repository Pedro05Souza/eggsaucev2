from tortoise.models import Model
from tortoise import fields
from tools.constants import PlayerTitles

__all__ = ["Player"]


class Player(Model):
    id = fields.UUIDField(pk=True)
    discord_user_id = fields.BigIntField()
    balance = fields.IntField(default=0)
    last_bought_title = fields.CharEnumField(PlayerTitles, null=True)
    next_salary_time = fields.DatetimeField(null=True)

    class Meta:
        table = "player"
