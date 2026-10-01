from typing import Optional
from discord import Member, app_commands
from discord.ext.commands import (
    Cog,
    Bot,
    hybrid_command,
    cooldown,
    BucketType,
    CooldownMapping,
    max_concurrency,
    parameter,
)
from usecases import (
    MarketUsecase,
    FarmUseCase,
    RenameFarmUsecase,
    BuyFarmerUseCase,
    InspectChickenUseCase,
    FeedAllChickenUsecase,
    FarmProfitUsecase,
    GiftChickenUsecase,
    RenameChickenUsecase,
    ChickenVaultUsecase,
    AddVaultUsecase,
    RemoveVaultUsecase,
    ChickenBattleUsecase,
    SellChickenUsecase,
    RedeemablesUsecase,
    BattleInfoUsecase,
    EvolveChickenUsecase,
    AscendancyUsecase,
    TradeChickenUsecase,
    ChickenDropRateUsecase,
    ChickenPricesUsecase,
)
from repositories import (
    FarmRepository,
    FarmRepositoryProtocol,
    PlayerRepositoryProtocol,
    PlayerRepository,
    CornfieldRepository,
)
from tools import (
    GlobalFarmCache,
    GlobalBotConfigCache,
    FarmCacheService,
    BotConfigCacheService,
    farm_chicken_autocomplete,
    member_farm_chicken_autocomplete,
    vault_chicken_autocomplete,
)
from tools.services import TransactionService, OnboardingService
from tools.constants import REGULAR_COMMAND_COOLDOWN, SPAM_COMMAND_COOLDOWN, MAX_GENERATED_CHICKENS
from eggsauce_context import EggsauceContext


class FarmController(  # pylint: disable=too-many-public-methods
    Cog,
    name="Farm",
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)},
    description="Commands to manage your farm, battle chickens, and more!",
):

    def __init__(
        self,
        bot: Bot,
        farm_cache: FarmCacheService,
        bot_config_cache: BotConfigCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        cornfield_repository: CornfieldRepository,
        transaction_service: TransactionService,
        onboarding_service: OnboardingService,
    ) -> None:
        self.bot = bot
        self.onboarding_service = onboarding_service
        self.farm_cache = farm_cache
        self.bot_config_cache = bot_config_cache
        self.farm_repository = farm_repository
        self.player_repository = player_repository
        self.cornfield_repository = cornfield_repository
        self.transaction_service = transaction_service

    @hybrid_command(
        name="market",
        aliases=["m"],
        description="🐔 Roll for a chicken in the market!",
        help=f"Generate **{MAX_GENERATED_CHICKENS}** random chickens available for purchase.",
    )
    @cooldown(1, SPAM_COMMAND_COOLDOWN, BucketType.user)
    async def market(self, ctx: EggsauceContext) -> None:
        market_usecase = MarketUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            self.player_repository,
            self.bot_config_cache,
            self.transaction_service,
            self.onboarding_service,
        )
        await market_usecase.market()

    @hybrid_command(
        name="farm",
        aliases=["f"],
        description="🐔 View your farm or someone else's!",
        help="Displays all chickens in a farm and their positions. Defaults to your farm unless another user is"
        + " specified.",
    )
    async def farm(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose farm you want to view. Defaults to the command author.",
        ),
    ) -> None:
        farm_usecase = FarmUseCase(
            ctx, self.farm_cache, self.farm_repository, self.player_repository, self.transaction_service, member
        )
        await farm_usecase.farm()

    @hybrid_command(
        name="renamefarm",
        aliases=["rf"],
        description="🐔 Rename your farm!",
        help="Change your farm's name",
    )
    async def rename_farm(
        self, ctx: EggsauceContext, new_name: str = parameter(description="The new name for your farm")
    ) -> None:
        rename_farm_usecase = RenameFarmUsecase(ctx, self.farm_cache, new_name, self.farm_repository)
        await rename_farm_usecase.rename_farm()

    @hybrid_command(
        name="buyfarmer",
        aliases=["bf"],
        description="🐔 Buy a farmer for your farm!",
        help="Buy farmers to gain permanent buffs.",
    )
    async def buy_farmer(self, ctx: EggsauceContext) -> None:
        buy_farmer_usecase = BuyFarmerUseCase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            self.player_repository,
            self.transaction_service,
        )
        await buy_farmer_usecase.buy_farmer()

    @hybrid_command(
        name="inspectchicken",
        aliases=["ic"],
        description="🐔 Retrieve detailed information about a specific chicken",
        help="Displays detailed stats of a chicken. Leave the position empty to pick it from a list.",
    )
    @app_commands.autocomplete(chicken=member_farm_chicken_autocomplete)
    async def inspect_chicken(
        self,
        ctx: EggsauceContext,
        chicken: Optional[int] = parameter(
            default=None, description="The chicken's position in the farm. Leave empty to pick from a list."
        ),
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose farm you want to view. Defaults to the command author.",
        ),
    ) -> None:
        chicken_info_usecase = InspectChickenUseCase(ctx, self.farm_cache, chicken, member)
        await chicken_info_usecase.inspect_chicken()

    @hybrid_command(
        name="feedall",
        aliases=["fa"],
        description="🐔 Feed all your chickens!",
        help="Feeds all chickens in your farm, increasing their happiness.",
    )
    async def feed_all_chicken(self, ctx: EggsauceContext) -> None:
        feed_all_chicken_usecase = FeedAllChickenUsecase(
            ctx,
            self.farm_repository,
            self.farm_cache,
            self.cornfield_repository,
            self.onboarding_service,
        )
        await feed_all_chicken_usecase.feed_all_chicken()

    @hybrid_command(
        name="farmprofit",
        aliases=["fp"],
        description="🐔 View your expected farm profits!",
        help="Displays the expected income of a farm. Defaults to your farm unless another user is specified.",
    )
    async def farm_profit(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose farm you want to view. Defaults to the command author.",
        ),
    ) -> None:
        farm_profit_usecase = FarmProfitUsecase(
            ctx,
            self.farm_cache,
            self.cornfield_repository,
            member,
            self.onboarding_service,
        )
        await farm_profit_usecase.farm_profit()

    @hybrid_command(
        name="giftchicken",
        aliases=["gc"],
        description="🐔 Gift a chicken to another player!",
        help="Transfers a chicken from your farm to another user. Leave the position empty to pick it from a list.",
    )
    @app_commands.autocomplete(chicken=farm_chicken_autocomplete)
    async def gift_chicken(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(description="The user you want to gift the chicken to."),
        chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken to gift. Leave empty to pick from a list."
        ),
    ) -> None:
        gift_chicken_usecase = GiftChickenUsecase(ctx, self.farm_cache, self.farm_repository, member, chicken)
        await gift_chicken_usecase.gift_chicken()

    @hybrid_command(
        name="renamechicken",
        aliases=["rc"],
        description="🐔 Rename a chicken in your farm!",
        help="Changes the name of a chicken in your farm. Leave the position empty to pick it from a list.",
    )
    @app_commands.autocomplete(chicken=farm_chicken_autocomplete)
    async def rename_chicken(
        self,
        ctx: EggsauceContext,
        new_name: str = parameter(description="The new name for the chicken (3-20 letters, numbers or _)."),
        chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken to rename. Leave empty to pick from a list."
        ),
    ) -> None:
        rename_chicken_usecase = RenameChickenUsecase(ctx, self.farm_cache, self.farm_repository, chicken, new_name)
        await rename_chicken_usecase.rename_chicken()

    @hybrid_command(
        name="vault",
        aliases=["v"],
        description="🐔 View your vaulted chickens!",
        help="Displays the currently vaulted chickens. Vaulted chickens are safe from battles,"
        + " devolving and do not lose happiness, but they can't produce any income.",
    )
    async def chicken_vault(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose vault you want to view. Defaults to the command author.",
        ),
    ) -> None:
        chicken_vault_usecase = ChickenVaultUsecase(ctx, self.farm_repository, member)
        await chicken_vault_usecase.chicken_vault()

    @hybrid_command(
        name="addvault",
        aliases=["av"],
        description="🐔 Add a chicken to your vault!",
        help="Moves a chicken from your farm to the vault. Leave the position empty to pick it from a list.",
    )
    @app_commands.autocomplete(chicken=farm_chicken_autocomplete)
    async def add_vault(
        self,
        ctx: EggsauceContext,
        chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken in the farm. Leave empty to pick from a list."
        ),
    ) -> None:
        add_vault_usecase = AddVaultUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            chicken,
        )
        await add_vault_usecase.add_vault()

    @hybrid_command(
        name="removevault",
        aliases=["rv"],
        description="🐔 Remove a chicken from your vault!",
        help="Moves a chicken from the vault back to your farm. If your farm is full, you pick a farm chicken"
        + " to swap into the vault. Leave the positions empty to pick from a list.",
    )
    @app_commands.autocomplete(vault_chicken=vault_chicken_autocomplete, swap_with=farm_chicken_autocomplete)
    async def remove_vault(
        self,
        ctx: EggsauceContext,
        vault_chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken in the vault. Leave empty to pick from a list."
        ),
        swap_with: Optional[int] = parameter(
            default=None,
            description="The position of a farm chicken to swap into the vault in its place.",
        ),
    ) -> None:
        remove_vault_usecase = RemoveVaultUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            vault_chicken,
            swap_with,
        )
        await remove_vault_usecase.remove_vault()

    @hybrid_command(
        name="battle",
        aliases=["b"],
        description="🐔 Battle a chicken against another player!",
        help="Queues your chicken for matchmaking."
        + " Battling with the **Guardian** Farmer will not give you extra chickens,"
        + " instead they will be cut off at the maximum amount of chickens you can have.",
    )
    @max_concurrency(100, BucketType.guild)
    async def chicken_battle(self, ctx: EggsauceContext) -> None:
        chicken_battle_usecase = ChickenBattleUsecase(
            ctx,
            self.farm_repository,
            self.farm_cache,
            self.player_repository,
        )
        await chicken_battle_usecase.queue()

    @hybrid_command(
        name="sellchicken",
        aliases=["sc"],
        description="🐔 Sell a chicken from your farm!",
        help="Sells a chicken for half of its original price,"
        + " unless you have the `Guardian` Farmer which lets you sell it for the full price."
        + " Leave the position empty to pick it from a list.",
    )
    @app_commands.autocomplete(chicken=farm_chicken_autocomplete)
    async def sell_chicken(
        self,
        ctx: EggsauceContext,
        chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken to sell. Leave empty to pick from a list."
        ),
    ) -> None:
        sell_chicken_usecase = SellChickenUsecase(
            ctx,
            self.farm_repository,
            self.player_repository,
            self.farm_cache,
            chicken,
        )
        await sell_chicken_usecase.sell_chicken()

    @hybrid_command(
        name="redeemables",
        aliases=["re"],
        description="🐔 View your chickens that are ready to be redeemed!",
        help="Every chicken that you gained in an event goes to your `redeemables` tab,"
        + " this includes the chickens that were gained ranking up.",
    )
    async def redeemables(self, ctx: EggsauceContext) -> None:
        redeemables_usecase = RedeemablesUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
        )
        await redeemables_usecase.redeemables()

    @hybrid_command(
        name="battleinfo",
        aliases=["bi"],
        description="🐔 View your battle status!",
        help="Displays the battle information of a user. Defaults to you.",
    )
    async def battle_info(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(default=lambda ctx: ctx.author, description="The user to view the battle info."),
    ) -> None:
        battle_info_usecase = BattleInfoUsecase(ctx, self.player_repository, member)
        await battle_info_usecase.battle_info()

    @hybrid_command(
        name="friendlybattle",
        aliases=["fb"],
        description="🐔 Battle against a friend without losing your rank",
        help="Sends a request for a friendly battle to the specified user."
        + " Friendly battles don't count as wins or losses and don't change your MMR.",
    )
    @max_concurrency(100, BucketType.guild)
    async def friendly_battle(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(description="The user you want to have a friendly battle with."),
    ) -> None:
        friendly_battle_usecase = ChickenBattleUsecase(
            ctx,
            self.farm_repository,
            self.farm_cache,
            self.player_repository,
            member,
        )
        await friendly_battle_usecase.queue()

    @hybrid_command(
        name="evolvechicken",
        aliases=["evolve"],
        description="🐔 Evolve two chickens of the same rarity!",
        help="Essentially lets you 'trade' two chickens of the"
        + " same rarity present in your farm for a single upper rarity chicken."
        + " The new chicken's **quality** is random, but never worse than the better of the two."
        + " Leave the positions empty to pick from a list that only shows chickens that can be paired.",
    )
    @app_commands.autocomplete(first_chicken=farm_chicken_autocomplete, second_chicken=farm_chicken_autocomplete)
    async def evolve_chicken(
        self,
        ctx: EggsauceContext,
        first_chicken: Optional[int] = parameter(
            default=None, description="The position of the first chicken. Leave empty to pick from a list."
        ),
        second_chicken: Optional[int] = parameter(
            default=None, description="The position of the second chicken. Leave empty to pick from a list."
        ),
    ) -> None:
        evolve_chicken_usecase = EvolveChickenUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            first_chicken,
            second_chicken,
        )
        await evolve_chicken_usecase.evolve_chicken()

    @hybrid_command(
        name="ascendancy",
        aliases=["asc"],
        description="🐔 Trade 8 Ascended chickens for an Ethereal one",
        help="Essentially lets you trade eight **ASCENDED** chickens for one **ETHEREAL** chicken."
        + " **ETHEREAL** chickens always come with 100% quality.",
    )
    async def ascendancy(self, ctx: EggsauceContext) -> None:
        ascendancy_usecase = AscendancyUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
        )
        await ascendancy_usecase.ascendancy()

    @hybrid_command(
        name="tradechicken",
        aliases=["tc"],
        description="🐔 Trade a chicken with another player!",
        help="Trade a chicken from your farm for one in another user's farm. They have to accept the trade."
        + " Leave the positions empty to pick from a list.",
    )
    @app_commands.autocomplete(your_chicken=farm_chicken_autocomplete, their_chicken=member_farm_chicken_autocomplete)
    async def trade_chicken(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(description="The user you want to trade with."),
        your_chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken you give. Leave empty to pick from a list."
        ),
        their_chicken: Optional[int] = parameter(
            default=None, description="The position of the chicken you want. Leave empty to pick from a list."
        ),
    ) -> None:
        trade_chicken_usecase = TradeChickenUsecase(
            ctx,
            self.farm_repository,
            self.farm_cache,
            your_chicken,
            member,
            their_chicken,
        )
        await trade_chicken_usecase.trade_chicken()

    @hybrid_command(
        name="chickenrates",
        aliases=["cr"],
        description="🐔 View the drop rates of chickens!",
        help="Displays the drop rates of chickens by rarity. The rates are used in the **market** command.",
    )
    async def chicken_drop_rates(self, ctx: EggsauceContext) -> None:
        chicken_drop_rate_usecase = ChickenDropRateUsecase(ctx)
        await chicken_drop_rate_usecase.chicken_drop_rates()

    @hybrid_command(
        name="chickenprices",
        aliases=["cp", "cps"],
        description="🐔 View the prices of chickens!",
        help="Displays the prices of chickens by rarity.",
    )
    async def chicken_prices(self, ctx: EggsauceContext) -> None:
        chicken_prices_usecase = ChickenPricesUsecase(ctx)
        await chicken_prices_usecase.get_chicken_prices()


async def setup(bot: Bot) -> None:
    player_repository = PlayerRepository()
    transaction_service = TransactionService(player_repository)
    await bot.add_cog(
        FarmController(
            bot,
            GlobalFarmCache,
            GlobalBotConfigCache,
            FarmRepository(),
            player_repository,
            CornfieldRepository(),
            transaction_service,
            OnboardingService(player_repository),
        )
    )
