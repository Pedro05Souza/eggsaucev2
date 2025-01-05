from random import Random
from datetime import datetime
from discord.ext.commands import Cog, hybrid_command, Bot, Context
from discord import Member, Message, VoiceState
from repositories import PlayerRepository
from tools import database_user, PointsService, CacheService
from usecases import BalanceUsecase, DonateUsecase, StealUsecase, GainPointsUsecase


class PlayerController(Cog):

    def __init__(
        self, bot: Bot, player_repo: PlayerRepository, points_service: PointsService
    ) -> None:
        self.bot = bot
        self.player_repo = player_repo
        self.points_service = points_service

    @hybrid_command(name="balance", aliases=["bal", "points", "p"])
    async def balance(self, ctx: Context, member: Member = None) -> None:
        member = member if member else ctx.author
        balance_usecase = BalanceUsecase(ctx, member, self.player_repo)
        await balance_usecase.get_player_balance()
        
    @hybrid_command(name="donate", aliases=["give"])
    @database_user()
    async def donate(self, ctx: Context, amount: int, recipient: Member) -> None:
        donate_usecase = DonateUsecase(
            ctx, ctx.player_entity, amount, recipient, self.player_repo
        )
        await donate_usecase.donate()

    @hybrid_command(name="steal", aliases=["rob"])
    @database_user()
    async def steal(self, ctx: Context, target: Member) -> None:
        random = Random()
        steal_usecase = StealUsecase(
            ctx, ctx.player_entity, target, self.player_repo, random
        )
        await steal_usecase.steal()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        g = GainPointsUsecase()

        await g.calculate_points_message(
            message.author.id, self.player_repo, self.points_service
        )

    @Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ) -> None:
        g = GainPointsUsecase()

        await g.calculate_points_voice(
            member.id, self.player_repo, self.points_service, before, after
        )

async def setup(bot: Bot) -> None:
    player_repo = PlayerRepository()
    points_service = PointsService(CacheService[int, datetime])
    await bot.add_cog(PlayerController(bot, player_repo, points_service))
