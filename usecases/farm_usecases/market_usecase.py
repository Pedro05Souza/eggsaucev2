from discord.ext.commands import Context
from tools import ChickenGeneratorService
from repositories import FarmRepository


class MarketUsecase:

    def __init__(
        self, ctx: Context, chicken_generator_service: ChickenGeneratorService, farm_repository: FarmRepository
    ) -> None:
        self.ctx = ctx
        self.chicken_generator_service = chicken_generator_service
        self.farm_repository = farm_repository
