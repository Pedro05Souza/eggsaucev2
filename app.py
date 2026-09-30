from eggsauce import Eggsauce
from tools import DatabaseStarterService, GlobalBotConfigCache, GlobalFarmCache
from usecases import HelpCommandUsecase


def main():
    DatabaseStarterService()
    bot = Eggsauce(GlobalBotConfigCache, GlobalFarmCache)
    bot.help_command = HelpCommandUsecase()
    bot.run()


if __name__ == "__main__":
    main()
