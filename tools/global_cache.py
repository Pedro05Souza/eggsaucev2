from repositories import PlayerRepository, BotConfigRepository
from .services import PlayerCacheService, BotConfigCacheService

__all__ = ['GlobalPlayerCache', 'GlobalBotConfigCache']

GlobalPlayerCache = PlayerCacheService(True, PlayerRepository())
GlobalBotConfigCache = BotConfigCacheService(False, BotConfigRepository())
