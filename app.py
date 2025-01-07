from eggsauce import Eggsauce
from tools import DatabaseStarterService


def main():
    DatabaseStarterService()
    bot = Eggsauce()
    bot.run()


if __name__ == "__main__":
    main()
