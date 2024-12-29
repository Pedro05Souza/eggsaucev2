import os
from dotenv import load_dotenv

class AppEnvVars():

    def get_env_var(self, enviroment_variable: str) -> str:
        load_dotenv()
        env_var = os.getenv(enviroment_variable)
        
        if env_var is None:
            raise ValueError(f"Environment variable {enviroment_variable} not set.")
        
        return env_var
        