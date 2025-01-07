from tortoise.models import Model
from tortoise import fields

__all__ = ["FarmRedeemables"]


class FarmRedeemables(Model):
    farm = fields.OneToOneField("models.Farm", pk=True)
    chicken = fields.ForeignKeyField(
        "models.Chicken", related_name="chicken_redeemables"
    )

    class Meta:
        table = "farm_redeemaables"
