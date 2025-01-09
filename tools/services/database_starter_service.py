from tortoise import Tortoise, run_async
from ..constants import TORTOISE_ORM
from ._singleton_meta import SingletonMeta

__all__ = ['DatabaseStarterService']

class DatabaseStarterService(metaclass=SingletonMeta):

    def __init__(self) -> None:
        run_async(self.__setup())

    async def __setup(self) -> None:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
