from repositories import PlayerRepository, BotConfigRepository, FarmRepository
from .services import PlayerCacheService, BotConfigCacheService, FarmCacheService

__all__ = [
    "GlobalPlayerCache",
    "GlobalBotConfigCache",
    "GlobalFarmCache",
]

GlobalPlayerCache = PlayerCacheService(False, PlayerRepository())
GlobalBotConfigCache = BotConfigCacheService(False, BotConfigRepository(), expiration_time=3600)
GlobalFarmCache = FarmCacheService(True, FarmRepository())
