from tortoise.models import Model
from tortoise import fields
from tools.constants import PlayerTitles

__all__ = ["Player"]


class Player(Model):
    id = fields.UUIDField(pk=True)
    discord_user_id = fields.BigIntField(unique=True)
    balance = fields.IntField(default=0)
    last_bought_title = fields.CharEnumField(PlayerTitles, default=PlayerTitles.EGG_NOVICE)
    next_salary_time = fields.DatetimeField()
    current_mmr = fields.IntField(default=0)
    highest_mmr = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    # Bitmask of the finished OnboardingStep values
    onboarding_steps = fields.IntField(default=0)
    # Null for players created before this field existed
    created_at = fields.DatetimeField(null=True, auto_now_add=True)

    class Meta:
        table = "player"
