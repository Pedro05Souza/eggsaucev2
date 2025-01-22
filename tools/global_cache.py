from repositories import PlayerRepository, BotConfigRepository, FarmRepository
from .services import PlayerCacheService, BotConfigCacheService, FarmCacheService

__all__ = ['GlobalPlayerCache', 'GlobalBotConfigCache', 'GlobalFarmCache']

GlobalPlayerCache = PlayerCacheService(True, PlayerRepository())
GlobalBotConfigCache = BotConfigCacheService(False, BotConfigRepository())
GlobalFarmCache = FarmCacheService(True, FarmRepository())
