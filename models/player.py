from tortoise.models import Model
from tortoise import fields

__all__ = ["Player"]


class Player(Model):
    id = fields.UUIDField(pk=True)
    discord_user_id = fields.BigIntField()
    balance = fields.IntField(default=0)
    role_values = fields.CharField(max_length=5, null=True)
    last_salary_time = fields.DatetimeField(null=True)

    class Meta:
        table = "player"
