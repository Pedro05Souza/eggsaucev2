from discord.ext.commands import Cog, hybrid_command, Bot, BucketType, CooldownMapping, parameter
from discord import Member, app_commands
from repositories import PlayerRepository, PlayerRepositoryProtocol
from tools import (
    BotConfigCacheService,
    GlobalBotConfigCache,
    spin_command_autocomplete,
)
from tools.constants import REGULAR_COMMAND_COOLDOWN, MIN_AMOUNT_SPIN, MIN_AMOUNT_TO_STEAL, STEAL_FAILURE_CHANCE
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
    command_attrs={
        "cooldown": CooldownMapping.from_cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user),
    },
    description="Commands to interact with the economy system.",
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
        name="balance",
        aliases=["bal", "points", "p"],
        description="💰 Check your balance or another user's!",
        help="Displays the amount of eggbux in the user's wallet, bank"
        + " and previews how long till the next salary drops.",
    )
    async def balance(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose balance is being checked. If not specified its the author.",
        ),
    ) -> None:
        balance_usecase = BalanceUsecase(ctx, self.player_repository, member)
        await balance_usecase.balance()

    @hybrid_command(
        name="donate",
        aliases=["give"],
        description="🤝 Share the love by donating eggbux to others!",
        help="Donate any amount to the specified user.",
    )
    async def donate(
        self,
        ctx: EggsauceContext,
        amount: int = parameter(description="The amount of the donation."),
        recipient: Member = parameter(description="The recipient of the donation."),
    ) -> None:
        donate_usecase = DonateUsecase(ctx, amount, recipient, self.player_repository)
        await donate_usecase.donate()

    @hybrid_command(
        name="steal",
        aliases=["rob"],
        description="🦹‍♂️ Steal some eggbux from another user!",
        help="Steal a random amount between **1%** to **25%** of the current money present in the user's wallet."
        + f" The user must have at least **{MIN_AMOUNT_TO_STEAL}** eggbux to be stolen from."
        + f" This command has a **{int(STEAL_FAILURE_CHANCE * 100)}** failure rate and doen't steal from the bank.",
    )
    async def steal(
        self, ctx: EggsauceContext, target: Member = parameter(description="The target to steal from.")
    ) -> None:
        steal_usecase = StealUsecase(ctx, target, self.player_repository)
        await steal_usecase.steal()

    @hybrid_command(
        name="spin",
        description="🎰 Spin the roulette wheel to win some eggbux!",
        help=f"Bet at least **{MIN_AMOUNT_SPIN}** eggbux. Choose a color (red, black, or green) and an amount to bet. "
        "If the wheel lands on your color, you win!"
        "Red and black have a combined **99%** chance of winning, while green has a **1%** chance.",
    )
    @app_commands.autocomplete(color_choice=spin_command_autocomplete)
    async def spin(
        self,
        ctx: EggsauceContext,
        color_choice: str = parameter(description="The color to bet on."),
        amount: int = parameter(description="The amount to bet."),
    ) -> None:
        spin_usecase = SpinUsecase(ctx, color_choice, amount, self.player_repository)
        await spin_usecase.spin()

    @hybrid_command(
        name="slots",
        description="🎰 Play the slot machine to win some eggbux!",
        help="Bet any amount of eggbux to play the slot machine. Match three fruits to win a jackpot, "
        "match two fruits to win a smaller prize, or lose your bet if no fruits match. "
        "\n\nPossible jackpots:\n"
        "🍇🍇🍇 (**12x**)\n"
        "🍋🍋🍋 (**9x**)\n"
        "🍒🍒🍒 (**7x**)\n"
        "🍊🍊🍊 (**5x**)\n"
        "🍉🍉🍉 (**3x**)\n\n"
        "Smaller prizes:\n"
        "🍇🍇 (**1.5x**)\n"
        "🍋🍋 (**1.4x**)\n"
        "🍒🍒 (**1.3x**)\n"
        "🍊🍊 (**1.2x**)\n"
        "🍉🍉 (**1.1x**).",
    )
    async def slots(self, ctx: EggsauceContext, amount: int = parameter(description="The amount to bet.")) -> None:
        slots_usecase = SlotsUsecase(ctx, amount, self.player_repository)
        await slots_usecase.slots()

    @hybrid_command(
        name="upgradebank",
        aliases=["ub"],
        description="🏦 Upgrade your bank limit!",
        help="Upgrade your bank limit to store more eggbux."
        " The upgrade costs an amount equal to your current bank capacity. "
        "Each upgrade increases your bank capacity by **10,000** eggbux.",
    )
    async def upgrade_bank_limit(self, ctx: EggsauceContext) -> None:
        upgrade_bank_limit_usecase = UpgradeBankUsecase(ctx, self.player_repository)
        await upgrade_bank_limit_usecase.upgrade_bank_limit()

    @hybrid_command(
        name="withdraw",
        aliases=["with", "w"],
        description="💸 Withdraw money from your bank account!",
        help="Withdraw any valid amount from your bank",
    )
    async def withdraw(
        self, ctx: EggsauceContext, amount: str = parameter(description="The amount to withdraw.")
    ) -> None:
        withdraw_usecase = WithdrawUsecase(ctx, amount, self.player_repository)
        await withdraw_usecase.withdraw()

    @hybrid_command(
        name="deposit",
        aliases=["dep"],
        descriptiom="💸Deposit money in your bank account!",
        help="Deposit any valid amount to your bank",
    )
    async def deposit(
        self, ctx: EggsauceContext, amount: str = parameter(description="The amount to deposit.")
    ) -> None:
        deposit_usecase = DepositUsecase(ctx, amount, self.player_repository)
        await deposit_usecase.deposit()

    @hybrid_command(
        name="upgradetitle",
        aliases=["bt"],
        description="🏆 Upgrade your title to earn more hourly income",
        help="Upgrade your title to increase your hourly income. Each title has a different price and income. "
        "The titles give a salary every **60** minutes. You can only upgrade to the next title in the sequence.",
    )
    async def upgrade_title(self, ctx: EggsauceContext) -> None:
        upgrade_title_usecase = UpgradeTitleUsecase(ctx, self.player_repository)
        await upgrade_title_usecase.upgrade_title()


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        PlayerController(
            bot,
            GlobalBotConfigCache,
            PlayerRepository(),
        )
    )
