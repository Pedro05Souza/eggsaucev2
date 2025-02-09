from tortoise.models import Model
from tortoise import fields
from tools.constants import PlayerTitles

__all__ = ["Player"]


class Player(Model):
    id = fields.UUIDField(pk=True)
    discord_user_id = fields.BigIntField()
    balance = fields.IntField(default=0)
    last_bought_title = fields.CharEnumField(PlayerTitles, default=PlayerTitles.EGG_NOVICE)
    next_salary_time = fields.DatetimeField()

    class Meta:
        table = "player"
