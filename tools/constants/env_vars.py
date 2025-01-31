import os
from typing import List
from json import loads
from dotenv import load_dotenv

__all__ = ["get_env_var"]


def get_env_var(enviroment_variable: str) -> str | List[str]:
    load_dotenv()
    env_var = os.getenv(enviroment_variable)

    if env_var is None:
        raise ValueError(f"Environment variable {enviroment_variable} not set.")

    if "LIST" in enviroment_variable:
        return list(loads(env_var))

    return env_var
