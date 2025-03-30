from eggsauce import Eggsauce
from tools import DatabaseStarterService, GlobalBotConfigCache, DatabaseBackupService
from usecases import HelpCommandUsecase


def main():
    DatabaseStarterService()
    bot = Eggsauce(GlobalBotConfigCache, database_backup_callback=DatabaseBackupService().start)
    bot.help_command = HelpCommandUsecase()
    bot.run()


if __name__ == "__main__":
    main()
