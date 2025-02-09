from eggsauce import Eggsauce
from tools import DatabaseStarterService, GlobalBotConfigCache, GlobalPlayerCache
from repositories import PlayerRepository


def main():
    DatabaseStarterService()
    bot = Eggsauce(GlobalBotConfigCache, PlayerRepository(), GlobalPlayerCache)
    bot.run()


if __name__ == "__main__":
    main()
