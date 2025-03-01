from typing import Optional
from discord.ext.commands import Cog, hybrid_command, Bot, BucketType, CooldownMapping
from discord import Member, app_commands
from repositories import PlayerRepository, PlayerRepositoryProtocol
from tools import (
    BotConfigCacheService,
    GlobalBotConfigCache,
    spin_command_autocomplete,
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


class PlayerController(
    Cog,
    name="Player",
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)},
):

    def __init__(
        self,
        bot: Bot,
        bot_config_cache: BotConfigCacheService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self.bot = bot
        self.bot_config_cache = bot_config_cache
        self.player_repository = player_repository

    @hybrid_command(
        name="balance", aliases=["bal", "points", "p"], description="💰 Check your balance or another user's!"
    )
    async def balance(self, ctx: EggsauceContext, member: Optional[Member] = None) -> None:
        balance_usecase = BalanceUsecase(ctx, self.player_repository, member)
        await balance_usecase.balance()

    @hybrid_command(name="donate", aliases=["give"], description="🤝 Share the love by donating eggbux to others!")
    async def donate(self, ctx: EggsauceContext, amount: int, recipient: Member) -> None:
        donate_usecase = DonateUsecase(ctx, amount, recipient, self.player_repository)
        await donate_usecase.donate()

    @hybrid_command(name="steal", aliases=["rob"], description="🦹‍♂️ Steal some eggbux from another user!")
    async def steal(self, ctx: EggsauceContext, target: Member) -> None:
        steal_usecase = StealUsecase(ctx, target, self.player_repository)
        await steal_usecase.steal()

    @hybrid_command(name="spin", description="🎰 Spin the roulette wheel to win some eggbux!")
    @app_commands.autocomplete(color_choice=spin_command_autocomplete)
    async def spin(self, ctx: EggsauceContext, color_choice: str, amount: int) -> None:
        spin_usecase = SpinUsecase(ctx, color_choice, amount, self.player_repository)
        await spin_usecase.spin()

    @hybrid_command(name="slots", description="🎰 Play the slot machine to win some eggbux!")
    async def slots(self, ctx: EggsauceContext, amount: int) -> None:
        slots_usecase = SlotsUsecase(ctx, amount, self.player_repository)
        await slots_usecase.slots()

    @hybrid_command(name="upgradebank", aliases=["ub"], description="🏦 Upgrade your bank limit!")
    async def upgrade_bank_limit(self, ctx: EggsauceContext) -> None:
        upgrade_bank_limit_usecase = UpgradeBankUsecase(ctx, self.player_repository)
        await upgrade_bank_limit_usecase.upgrade_bank_limit()

    @hybrid_command(name="withdraw", aliases=["with", "w"], description="💸 Withdraw money from your bank account!")
    async def withdraw(self, ctx: EggsauceContext, amount: str) -> None:
        withdraw_usecase = WithdrawUsecase(ctx, amount, self.player_repository)
        await withdraw_usecase.withdraw()

    @hybrid_command(name="deposit", aliases=["dep"], descriptiom="💸Deposit money in your bank account!")
    async def deposit(self, ctx: EggsauceContext, amount: str) -> None:
        deposit_usecase = DepositUsecase(ctx, amount, self.player_repository)
        await deposit_usecase.deposit()

    @hybrid_command(name="upgradetitle", aliases=["bt"], description="🏆 Upgrade your title to earn more hourly income")
    async def buy_title(self, ctx: EggsauceContext) -> None:
        buy_title_usecase = UpgradeTitleUsecase(ctx, self.player_repository)
        await buy_title_usecase.buy_title()


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        PlayerController(
            bot,
            GlobalBotConfigCache,
            PlayerRepository(),
        )
    )
