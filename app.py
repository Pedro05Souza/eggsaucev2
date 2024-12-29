from eggsauce import Eggsauce
from tools.app_env_vars import AppEnvVars
from tools.database_starter import DatabaseStarter

def main():
    app_env_vars = AppEnvVars()
    DatabaseStarter(app_env_vars)
    bot = Eggsauce(app_env_vars)
    bot.run()
    
if __name__ == "__main__":
    main()