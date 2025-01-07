from repositories import PlayerRepository, BotConfigRepository
from .services import PlayerCacheService, BotConfigCacheService

__all__ = ['GlobalPlayerCache']

GlobalPlayerCache = PlayerCacheService(PlayerRepository())
GlobalBotConfigCache = BotConfigCacheService(BotConfigRepository())
