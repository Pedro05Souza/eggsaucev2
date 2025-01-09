from eggsauce import Eggsauce
from tools import DatabaseStarterService, GlobalBotConfigCache


def main():
    DatabaseStarterService()
    bot = Eggsauce(GlobalBotConfigCache)
    bot.run()


if __name__ == "__main__":
    main()
