from tortoise.models import Model
from tortoise import fields

__all__ = ["Player"]

class Player(Model):
    id = fields.UUIDField(pk=True)
    discord_user_id = fields.BigIntField()
    balance = fields.IntField()
    role_values = fields.CharField(max_length=5)
    last_salary_time = fields.DatetimeField()

    class Meta:
        table = "player"
