from .env_vars import get_env_var

__all__ = ["TORTOISE_ORM"]

TORTOISE_ORM = {
    "connections": {"default": get_env_var("DATABASE_URL")},
    "apps": {"models": {"models": ["models", "aerich.models"], "default_connection": "default"}},
}
