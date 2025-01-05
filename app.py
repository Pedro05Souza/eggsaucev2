from eggsauce import Eggsauce
from tools.database_starter import DatabaseStarter


def main():
    DatabaseStarter()
    bot = Eggsauce()
    bot.run()


if __name__ == "__main__":
    main()
