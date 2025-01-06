from datetime import datetime
from discord.ext.commands import Cog, hybrid_command, Bot, Context
from discord import Member, Message, VoiceState, app_commands
from tools import (
    database_user,
    PointsService,
    PlayerCacheService,
    CacheService,
    GlobalPlayerCache,
    spin_command_autocomplete,
)
from usecases import BalanceUsecase, DonateUsecase, StealUsecase, GainPointsUsecase, SpinUsecase


class PlayerController(Cog):

    def __init__(self, bot: Bot, player_cache: PlayerCacheService, points_service: PointsService) -> None:
        self.bot = bot
        self.player_cache = player_cache
        self.points_service = points_service

    @hybrid_command(name="balance", aliases=["bal", "points", "p"])
    async def balance(self, ctx: Context, member: Member = None) -> None:
        member = member if member else ctx.author
        balance_usecase = BalanceUsecase(ctx, member, self.player_cache)
        await balance_usecase.get_player_balance()

    @hybrid_command(name="donate", aliases=["give"])
    @database_user()
    async def donate(self, ctx: Context, amount: int, recipient: Member) -> None:
        donate_usecase = DonateUsecase(ctx, ctx.player_entity, amount, recipient, self.player_cache)
        await donate_usecase.donate()

    @hybrid_command(name="steal", aliases=["rob"])
    @database_user()
    async def steal(self, ctx: Context, target: Member) -> None:
        steal_usecase = StealUsecase(ctx, ctx.player_entity, target, self.player_cache)
        await steal_usecase.steal()

    @hybrid_command(name="spin")
    @app_commands.autocomplete(color_choice=spin_command_autocomplete)
    @database_user()
    async def spin(self, ctx: Context, color_choice: str, amount_betted: int) -> None:
        spin_usecase = SpinUsecase(ctx, ctx.player_entity, self.player_cache, color_choice, amount_betted)
        await spin_usecase.spin()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        g = GainPointsUsecase()

        await g.calculate_points_message(message.author.id, self.player_cache, self.points_service)

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        g = GainPointsUsecase()

        await g.calculate_points_voice(member.id, self.player_cache, self.points_service, before, after)


async def setup(bot: Bot) -> None:
    points_service = PointsService(CacheService[int, datetime])
    await bot.add_cog(PlayerController(bot, GlobalPlayerCache, points_service))
