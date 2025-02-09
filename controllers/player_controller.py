from typing import Optional
from discord.ext.commands import Cog, hybrid_command, Bot, cooldown, before_invoke, BucketType
from discord import Member, app_commands
from repositories import PlayerRepository, PlayerRepositoryProtocol, FarmRepository, FarmRepositoryProtocol
from tools import (
    FarmCacheService,
    PlayerCacheService,
    AwayTimeEarningsService,
    BotConfigCacheService,
    GlobalPlayerCache,
    GlobalBotConfigCache,
    GlobalFarmCache,
    spin_command_autocomplete,
    ensure_player,
    is_using_valid_channel,
    mark_as_updatable,
)
from tools.constants import REGULAR_COMMAND_COOLDOWN
from usecases import (
    BalanceUsecase,
    DonateUsecase,
    StealUsecase,
    SpinUsecase,
    UpgradeBankUsecase,
    SlotsUsecase,
    WithdrawUsecase,
    DepositUsecase,
    UpgradeTitleUsecase,
)
from eggsauce_context import EggsauceContext


class PlayerController(Cog):

    def __init__(
        self,
        bot: Bot,
        player_cache: PlayerCacheService,
        bot_config_cache: BotConfigCacheService,
        player_repository: PlayerRepositoryProtocol,
        away_time_earnings_service: AwayTimeEarningsService,
        farm_repository: FarmRepositoryProtocol,
        farm_cache: FarmCacheService,
    ) -> None:
        self.bot = bot
        self.player_cache = player_cache
        self.bot_config_cache = bot_config_cache
        self.player_repository = player_repository
        self.away_time_earnings_service = away_time_earnings_service
        self.farm_repository = farm_repository
        self.farm_cache = farm_cache

    async def _ensure_database_player_decorator(self, ctx: EggsauceContext) -> None:
        await ensure_player(ctx, self.player_cache, self.player_repository)

    async def _mark_as_updatable_decorator(self, ctx: EggsauceContext) -> None:
        await mark_as_updatable(
            ctx,
            self.player_cache,
            self.player_repository,
            self.farm_cache,
            self.farm_repository,
            self.away_time_earnings_service,
        )

    @hybrid_command(
        name="balance", aliases=["bal", "points", "p"], description="💰 Check your balance or another user's!"
    )
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_mark_as_updatable_decorator)
    async def balance(self, ctx: EggsauceContext, member: Optional[Member] = None) -> None:
        balance_usecase = BalanceUsecase(ctx, self.player_cache, self.player_repository)
        await balance_usecase.balance()

    @hybrid_command(name="donate", aliases=["give"], description="🤝 Share the love by donating eggbux to others!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def donate(self, ctx: EggsauceContext, amount: int, recipient: Member) -> None:
        donate_usecase = DonateUsecase(ctx, amount, recipient, self.player_cache, self.player_repository)
        await donate_usecase.donate()

    @hybrid_command(name="steal", aliases=["rob"], description="🦹‍♂️ Steal some eggbux from another user!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def steal(self, ctx: EggsauceContext, target: Member) -> None:
        steal_usecase = StealUsecase(ctx, target, self.player_cache, self.player_repository)
        await steal_usecase.steal()

    @hybrid_command(name="spin", description="🎰 Spin the roulette wheel to win some eggbux!")
    @app_commands.autocomplete(color_choice=spin_command_autocomplete)
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def spin(self, ctx: EggsauceContext, color_choice: str, amount: int) -> None:
        spin_usecase = SpinUsecase(ctx, self.player_cache, color_choice, amount, self.player_repository)
        await spin_usecase.spin()

    @hybrid_command(name="slots", description="🎰 Play the slot machine to win some eggbux!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def slots(self, ctx: EggsauceContext, amount: int) -> None:
        slots_usecase = SlotsUsecase(ctx, self.player_cache, amount, self.player_repository)
        await slots_usecase.slots()

    @hybrid_command(name="upgradebank", aliases=["ub"], description="🏦 Upgrade your bank limit!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def upgrade_bank_limit(self, ctx: EggsauceContext) -> None:
        upgrade_bank_limit_usecase = UpgradeBankUsecase(ctx, self.player_cache, self.player_repository)
        await upgrade_bank_limit_usecase.upgrade_bank_limit()

    @hybrid_command(name="withdraw", aliases=["with", "w"], description="💸 Withdraw money from your bank account!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def withdraw(self, ctx: EggsauceContext, amount: str) -> None:
        withdraw_usecase = WithdrawUsecase(ctx, self.player_cache, amount, self.player_repository)
        await withdraw_usecase.withdraw()

    @hybrid_command(name="deposit", aliases=["dep"], descriptiom="💸Deposit money in your bank account!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def deposit(self, ctx: EggsauceContext, amount: str) -> None:
        deposit_usecase = DepositUsecase(ctx, self.player_cache, amount, self.player_repository)
        await deposit_usecase.deposit()

    @hybrid_command(name="upgradetitle", aliases=["bt"], description="🏆 Upgrade your title to earn more hourly income")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_ensure_database_player_decorator)
    async def buy_title(self, ctx: EggsauceContext) -> None:
        buy_title_usecase = UpgradeTitleUsecase(ctx, self.player_cache, self.player_repository)
        await buy_title_usecase.buy_title()

    async def cog_check(self, ctx: EggsauceContext) -> bool:  # type: ignore
        return await is_using_valid_channel(ctx, self.bot_config_cache)

async def setup(bot: Bot) -> None:
    away_time_earnings_service = AwayTimeEarningsService()
    await bot.add_cog(
        PlayerController(
            bot,
            GlobalPlayerCache,
            GlobalBotConfigCache,
            PlayerRepository(),
            away_time_earnings_service,
            FarmRepository(),
            GlobalFarmCache,
        )
    )
