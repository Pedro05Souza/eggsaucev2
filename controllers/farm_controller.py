from typing import Optional
from discord import Member
from discord.ext.commands import (
    Cog,
    Bot,
    hybrid_command,
    command,
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
from tools import GlobalFarmCache, GlobalBotConfigCache, FarmCacheService, BotConfigCacheService, ensure_author_farm
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
    ) -> None:
        self.bot = bot
        self.farm_cache = farm_cache
        self.bot_config_cache = bot_config_cache
        self.farm_repository = farm_repository
        self.player_repository = player_repository
        self.cornfield_repository = cornfield_repository

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
        )
        await market_usecase.market()

    @command(
        name="farm",
        aliases=["f"],
        help="Displays all chickens in a farm. Defaults to your farm unless another user is specified.",
    )
    async def farm(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose farm you want to view. Defaults to the command author.",
        ),
    ) -> None:
        farm_usecase = FarmUseCase(ctx, self.farm_cache, self.farm_repository, self.player_repository, member)
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
        )
        await buy_farmer_usecase.buy_farmer()

    @hybrid_command(
        name="inspectchicken",
        aliases=["ic"],
        description="🐔 Retrieve detailed information about a specific chicken",
        help="Displays detailed stats of a chicken by its position in your farm.",
    )
    async def inspect_chicken(
        self,
        ctx: EggsauceContext,
        position: int = parameter(description="The position of the chicken in your farm."),
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose farm you want to view. Defaults to the command author.",
        ),
    ) -> None:
        chicken_info_usecase = InspectChickenUseCase(ctx, self.farm_cache, position, member)
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
        )
        await farm_profit_usecase.farm_profit()

    @hybrid_command(
        name="giftchicken",
        aliases=["gc"],
        description="🐔 Gift a chicken to another player!",
        help="Transfers a chicken from your farm to another user.",
    )
    async def gift_chicken(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(description="The user you want to gift the chicken to"),
        position: int = parameter(description="The position of the chicken in your farm that you'd want to give."),
    ) -> None:
        gift_chicken_usecase = GiftChickenUsecase(ctx, self.farm_cache, self.farm_repository, member, position)
        await gift_chicken_usecase.gift_chicken()

    @hybrid_command(
        name="renamechicken",
        aliases=["rc"],
        description="🐔 Rename a chicken in your farm!",
        help="Changes the name of a chicken in your farm.",
    )
    async def rename_chicken(
        self,
        ctx: EggsauceContext,
        position: int = parameter(description="The position of the chicken in your farm."),
        new_name: str = parameter(description="The new name for the chicken"),
    ) -> None:
        rename_chicken_usecase = RenameChickenUsecase(ctx, self.farm_cache, self.farm_repository, position, new_name)
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
        help="Moves a chicken from your farm to the vault.",
    )
    async def add_vault(
        self, ctx: EggsauceContext, position: int = parameter(description="The position of the chicken in the farm.")
    ) -> None:
        add_vault_usecase = AddVaultUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            position,
        )
        await add_vault_usecase.add_vault()

    @hybrid_command(
        name="removevault",
        aliases=["rv"],
        description="🐔 Remove a chicken from your vault!",
        help="Moves a chicken from the vault back to your farm.",
    )
    async def remove_vault(
        self,
        ctx: EggsauceContext,
        position: int = parameter(description="The position of the chicken in the vault."),
        farm_position: Optional[int] = parameter(
            default=None,
            description="An optional argument that switches the selected chicken from the farm to the vault.",
        ),
    ) -> None:
        remove_vault_usecase = RemoveVaultUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            position,
            farm_position,
        )
        await remove_vault_usecase.remove_vault()

    @hybrid_command(
        name="battle",
        aliases=["b"],
        description="🐔 Battle a chicken against another player!",
        help="Queues your chicken for matchmaking."
        + " Battiling with the **Guardian** Farmer will not give you extra chickens,"
        + " instead they will be cut off to the maximum amount of chickens you can have.",
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
        + " unless you have the `Guardian` Farmer which lets you sell it for the full price.",
    )
    async def sell_chicken(
        self, ctx: EggsauceContext, position: int = parameter(description="The position of the chicken")
    ) -> None:
        sell_chicken_usecase = SellChickenUsecase(
            ctx,
            self.farm_repository,
            self.player_repository,
            self.farm_cache,
            position,
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
        help="Displays the battle ifnromation of the user.",
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
        + " Friendly battles do not increase your losses or wins nor they gie you MMR",
    )
    @max_concurrency(100, BucketType.guild)
    async def friendly_battle(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(description="The user you want yo have a friendly battle with"),
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
        + " All the status in the new chicken are randomized, this includes **quality**.",
    )
    async def evolve_chicken(
        self,
        ctx: EggsauceContext,
        first_position: int = parameter(description="The position of the first chicken in the farm"),
        second_position: int = parameter(description="The position of the second chicken in the farm"),
    ) -> None:
        evolve_chicken_usecase = EvolveChickenUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            first_position,
            second_position,
        )
        await evolve_chicken_usecase.evolve_chicken()

    @hybrid_command(
        name="ascendancy",
        aliases=["asc"],
        description="🐔 Trade 8 Ascended chickebs for an ethereal one",
        help="Essentially lets you trade eight **ASCENDED** chickens for one **ETHEREAL** chicken."
        + "**ETHEREAL** chickens always come with 100% quality.",
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
        help="Trade a chicken from your farm with another user.",
    )
    async def trade_chicken(
        self,
        ctx: EggsauceContext,
        member: Member = parameter(description="The user you want to trade with"),
        farm_position: int = parameter(description="The position of the chicken in your farm"),
        user_farm_position: int = parameter(description="The position of the chicken in the user's farm"),
    ) -> None:
        trade_chicken_usecase = TradeChickenUsecase(
            ctx,
            self.farm_repository,
            self.farm_cache,
            farm_position,
            member,
            user_farm_position,
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
        aliases=["cps"],
        description="🐔 View the prices of chickens!",
        help="Displays the prices of chickens by rarity.",
    )
    async def chicken_prices(self, ctx: EggsauceContext) -> None:
        chicken_prices_usecase = ChickenPricesUsecase(ctx)
        await chicken_prices_usecase.get_chicken_prices()

    async def cog_before_invoke(self, ctx: EggsauceContext) -> None:  # type: ignore
        await ensure_author_farm(
            ctx,
            self.farm_cache,
            self.farm_repository,
            self.cornfield_repository,
            self.player_repository,
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        FarmController(
            bot,
            GlobalFarmCache,
            GlobalBotConfigCache,
            FarmRepository(),
            PlayerRepository(),
            CornfieldRepository(),
        )
    )
