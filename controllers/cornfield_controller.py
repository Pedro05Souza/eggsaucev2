from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, before_invoke
from tools import (
    ensure_farm,
    ensure_cornfield_and_attach,
    GlobalFarmCache,
    FarmCacheService,
    ensure_cornfield,
    mark_as_updatable_corn,
)
from usecases import CornFieldUsecase
from repositories import FarmRepositoryProtocol, CornfieldRepositoryProtocol, FarmRepository, CornfieldRepository

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext


class CornfieldController(Cog):

    def __init__(
        self,
        bot: Bot,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        cornfield_repository: CornfieldRepositoryProtocol,
    ) -> None:
        self.bot = bot
        self.farm_cache_service = farm_cache_service
        self.farm_repository = farm_repository
        self.cornfield_repository = cornfield_repository

    async def _mark_as_updatable_cornfield_decorator(self, ctx: "EggsauceContext") -> None:
        await ensure_farm(ctx, self.farm_cache_service, self.farm_repository, self.cornfield_repository)
        await ensure_cornfield(ctx, self.cornfield_repository)
        await mark_as_updatable_corn(ctx, self.cornfield_repository)

    @hybrid_command(name="cornfield", aliases=["corn"], description="🌽 Visit the cornfield to earn some eggbux!")
    @before_invoke(_mark_as_updatable_cornfield_decorator)
    async def cornfield(self, ctx: "EggsauceContext", member: Optional[Member] = None) -> None:
        cornfield_usecase = CornFieldUsecase(ctx)
        await cornfield_usecase.cornfield()

    async def cog_before_invoke(self, ctx: "EggsauceContext") -> None:  # type: ignore
        await ensure_farm(ctx, self.farm_cache_service, self.farm_repository, self.cornfield_repository)
        await ensure_cornfield_and_attach(ctx, self.cornfield_repository)


async def setup(bot: Bot) -> None:
    await bot.add_cog(CornfieldController(bot, GlobalFarmCache, FarmRepository(), CornfieldRepository()))
