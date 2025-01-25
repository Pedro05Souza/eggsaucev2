from typing import Optional
from datetime import datetime
from discord.ext.commands import Cog, hybrid_command, Bot, Context, cooldown, before_invoke, BucketType
from discord import Member, Message, VoiceState, app_commands
from tools import (
    AwayTimeEarningsService,
    PointsService,
    PlayerCacheService,
    BotConfigCacheService,
    LRUCacheService,
    GlobalPlayerCache,
    GlobalBotConfigCache,
    spin_command_autocomplete,
    ensure_database_user,
    is_using_valid_channel,
)
from tools.constants import REGULAR_COMMAND_COOLDOWN
from usecases import (
    BalanceUsecase,
    DonateUsecase,
    StealUsecase,
    GainPointsUsecase,
    SpinUsecase,
    UpgradeBankUsecase,
    SlotsUsecase,
    WithdrawUsecase,
    DepositUsecase,
    BuyTitleUsecase,
)


class PlayerController(Cog):

    def __init__(
        self,
        bot: Bot,
        player_cache: PlayerCacheService,
        points_service: PointsService,
        away_time_earnings_service: AwayTimeEarningsService,
        bot_config_cache: BotConfigCacheService,
    ) -> None:
        self.bot = bot
        self.player_cache = player_cache
        self.points_service = points_service
        self.away_time_earnings_service = away_time_earnings_service
        self.bot_config_cache = bot_config_cache

    async def _ensure_database_player_decorator(self, ctx: Context) -> None:
        await ensure_database_user(ctx, self.player_cache)

    @hybrid_command(
        name="balance", aliases=["bal", "points", "p"], description="💰 Check your balance or another user's!"
    )
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def balance(self, ctx: Context, member: Optional[Member] = None) -> None:
        balance_usecase = BalanceUsecase(ctx, member, self.player_cache, self.away_time_earnings_service)
        await balance_usecase.balance()

    @hybrid_command(name="donate", aliases=["give"], description="🤝 Share the love by donating eggbux to others!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def donate(self, ctx: Context, amount: int, recipient: Member) -> None:
        donate_usecase = DonateUsecase(ctx, ctx.player_entity, amount, recipient, self.player_cache)
        await donate_usecase.donate()

    @hybrid_command(name="steal", aliases=["rob"], description="🦹‍♂️ Steal some eggbux from another user!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def steal(self, ctx: Context, target: Member) -> None:
        steal_usecase = StealUsecase(ctx, ctx.player_entity, target, self.player_cache)
        await steal_usecase.steal()

    @hybrid_command(name="spin", description="🎰 Spin the roulette wheel to win some eggbux!")
    @app_commands.autocomplete(color_choice=spin_command_autocomplete)
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def spin(self, ctx: Context, color_choice: str, amount: int) -> None:
        spin_usecase = SpinUsecase(ctx, ctx.player_entity, self.player_cache, color_choice, amount)
        await spin_usecase.spin()

    @hybrid_command(name="slots", description="🎰 Play the slot machine to win some eggbux!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def slots(self, ctx: Context, amount: int) -> None:
        slots_usecase = SlotsUsecase(ctx, ctx.player_entity, self.player_cache, amount)
        await slots_usecase.slots()

    @hybrid_command(name="upgradebank", aliases=["ub"], description="🏦 Upgrade your bank limit!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def upgrade_bank_limit(self, ctx: Context) -> None:
        upgrade_bank_limit_usecase = UpgradeBankUsecase(ctx, ctx.player_entity, self.player_cache)
        await upgrade_bank_limit_usecase.upgrade_bank_limit()

    @hybrid_command(name="withdraw", aliases=["with"], description="💸 Withdraw money from your bank account!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def withdraw(self, ctx: Context, amount: int) -> None:
        withdraw_usecase = WithdrawUsecase(ctx, ctx.player_entity, self.player_cache, amount)
        await withdraw_usecase.withdraw()

    @hybrid_command(name="deposit", aliases=["dep"], descriptiom="💸Deposit money in your bank account!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def deposit(self, ctx: Context, amount: int) -> None:
        deposit_usecase = DepositUsecase(ctx, ctx.player_entity, self.player_cache, amount)
        await deposit_usecase.deposit()

    @hybrid_command(name="buytitle", aliases=["bt"], description="🏆 Buy a new title to earn hourly income!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def buy_title(self, ctx: Context) -> None:
        buy_title_usecase = BuyTitleUsecase(ctx, ctx.player_entity, self.player_cache)
        await buy_title_usecase.buy_title()

    async def cog_check(self, ctx: Context) -> bool: # type: ignore
        return await is_using_valid_channel(ctx, self.bot_config_cache)

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
    points_service = PointsService(LRUCacheService[int, datetime]())
    away_time_earnings_service = AwayTimeEarningsService()
    await bot.add_cog(
        PlayerController(bot, GlobalPlayerCache, points_service, away_time_earnings_service, GlobalBotConfigCache)
    )
