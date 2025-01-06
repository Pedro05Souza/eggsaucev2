from repositories import PlayerRepository
from .services import PlayerCacheService


__all__ = ['GlobalPlayerCache']

GlobalPlayerCache = PlayerCacheService(PlayerRepository())
