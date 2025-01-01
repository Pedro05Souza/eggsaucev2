from .app_env_vars import get_env_var

TORTOISE_ORM = {
    "connections": {"default": get_env_var("DATABASE_URL")},
    "apps": {"models": {"models": ["models", "aerich.models"], "default_connection": "default"}},
}
