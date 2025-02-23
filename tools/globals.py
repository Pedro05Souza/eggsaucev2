from repositories import BotConfigRepository, FarmRepository
from .services import BotConfigCacheService, FarmCacheService

__all__ = [
    "GlobalBotConfigCache",
    "GlobalFarmCache",
]

GlobalBotConfigCache = BotConfigCacheService(False, BotConfigRepository(), expiration_time=3600)
GlobalFarmCache = FarmCacheService(True, FarmRepository())
