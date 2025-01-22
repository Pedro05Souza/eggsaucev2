from tortoise.models import Model
from tortoise import fields

__all__ = ["BankPlayer"]


class BankPlayer(Model):
    player = fields.OneToOneField("models.Player", pk=True, related_name="bank_player")
    balance = fields.IntField(default=400)
    upgrade_level = fields.IntField(default=1)

    class Meta:
        table = "bank_player"
