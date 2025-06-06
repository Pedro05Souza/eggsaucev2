from discord.ext.commands import Cog, Bot, command
from discord import Member
from usecases import ReloadCogsUsecase, DevPanelUsecase, GiveMoneyUsecase
from repositories import PlayerRepositoryProtocol, PlayerRepository
from tools import dev_only, get_logger
from eggsauce_context import EggsauceContext


class DeveloperController(Cog, name="Developer", command_attrs={"hidden": True}):

    def __init__(self, bot: Bot, player_repository: PlayerRepositoryProtocol) -> None:
        self.bot = bot
        self.player_repository = player_repository
        self.logger = get_logger(__name__)

    @command(name="reload", aliases=["r"])
    @dev_only()
    async def reload(self, _: EggsauceContext) -> None:
        reload_usecase = ReloadCogsUsecase(self.bot)
        await reload_usecase.reload_cogs()

    @command(name="sync")
    @dev_only()
    async def sync(self, _: EggsauceContext) -> None:
        await self.bot.tree.sync()

    @command("devpanel", aliases=["dp"])
    @dev_only()
    async def devpanel(self, ctx: EggsauceContext) -> None:
        dev_panel_usecase = DevPanelUsecase(ctx)
        await dev_panel_usecase.dev_panel()
        
    @command(name="givemoney", aliases=["gm"])
    @dev_only()
    async def give_money(self, ctx: EggsauceContext, member: Member, amount: int) -> None:
        give_money_usecase = GiveMoneyUsecase(ctx, self.player_repository, member, amount)
        await give_money_usecase.give_money(amount)

    async def cog_after_invoke(self, ctx: EggsauceContext) -> None: # type: ignore
        if ctx.author and ctx.command and ctx.guild:
            self.logger.info(
                "User %s (%s) used command %s in guild %s (%s)",
                ctx.author,
                ctx.author.id,
                ctx.command,
                ctx.guild,
                ctx.guild.id,
            )
        else:
            self.logger.warning("Context is missing required attributes for logging.")


async def setup(bot: Bot) -> None:
    await bot.add_cog(DeveloperController(bot, PlayerRepository()))
