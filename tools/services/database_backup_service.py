import os
import asyncio
from datetime import datetime, timedelta
from scheduler.asyncio import Scheduler
from tools.utils import get_logger
from tools.constants import get_env_var

__all__ = ["DatabaseBackupService"]


class DatabaseBackupService:

    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    async def start(self) -> None:
        is_dev = get_env_var("ENVIRONMENT") == "DEV"

        if is_dev:
            self._logger.info("Skipping database backup: Service is disabled in the development environment.")
            return

        loop = asyncio.get_running_loop()
        scheduler = Scheduler(loop=loop)  # type: ignore

        scheduler.cyclic(
            timedelta(hours=2),
            self._backup_database,
        )

        asyncio.create_task(self._keep_alive())

    async def _keep_alive(self) -> None:
        while True:
            await asyncio.sleep(60)

    async def _backup_database(self) -> None:
        self._logger.info("Starting database backup...")
        now = datetime.now()

        backup_filename = f"./backups/eggsauce_db_{now.strftime('%Y%m%d_%H%M%S')}.dump"

        process = await asyncio.create_subprocess_exec(
            "pg_dump",
            "-h",
            "eggsauce_db",
            "-U",
            "postgres",
            "-F",
            "c",
            "-f",
            backup_filename,
            "eggsauce",
            env={**os.environ, "PGPASSWORD": os.getenv("DATABASE_PASSWORD", "")},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            self._logger.error("Database backup failed: %s", stderr.decode().strip())
            return
        self._logger.info("Database backup completed successfully: %s", backup_filename)
