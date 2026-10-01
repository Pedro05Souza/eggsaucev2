from discord.ext.commands import Cog, Bot, hybrid_command, CooldownMapping, BucketType
from repositories import PlayerRepository, PlayerRepositoryProtocol
from tools.constants import REGULAR_COMMAND_COOLDOWN
from usecases import GuideUsecase
from eggsauce_context import EggsauceContext


class GuideController(
    Cog,
    name="Guide",
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)},
    description="New here? Start with the guide!",
):

    def __init__(self, bot: Bot, player_repository: PlayerRepositoryProtocol) -> None:
        self.bot = bot
        self.player_repository = player_repository

    @hybrid_command(
        name="guide",
        aliases=["tutorial", "start"],
        description="📖 Learn how Eggsauce works and track your first steps!",
        help="Explains how the game works and shows your **Getting started** checklist."
        + " Each step you finish pays eggbux, with a bonus for finishing them all.",
    )
    async def guide(self, ctx: EggsauceContext) -> None:
        guide_usecase = GuideUsecase(ctx, self.player_repository)
        await guide_usecase.guide()


async def setup(bot: Bot) -> None:
    await bot.add_cog(GuideController(bot, PlayerRepository()))
