from tortoise import Tortoise, run_async
from tools.app_env_vars import AppEnvVars


class DatabaseStarter:

    def __init__(self, app_env_vars: AppEnvVars) -> None:
        self.app_env_vars = app_env_vars
        run_async(self.__setup())

    def __retrieve_config(self) -> dict:
        database_url = self.app_env_vars.get_env_var("DATABASE_URL")
        print(f"Database URL: {database_url}")

        return {
            "connections": {"default": database_url},
            "apps": {"models": {"models": ["models"], "default_connection": "default"}},
        }

    async def __setup(self) -> None:
        config = self.__retrieve_config()
        await Tortoise.init(config)
        await Tortoise.generate_schemas()
