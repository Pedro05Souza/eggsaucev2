import subprocess
import os
import click
from dotenv import load_dotenv


@click.group()
def cli():  # pylint: disable=no-self-argument,no-method-argument
    pass


@cli.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "prod"]),
    default="dev",
    help="🚀 Run the bot in the specified environment (dev or prod)",
)
def run(env: str) -> None:  # pylint: disable=no-self-argument,no-method-argument
    os.environ["ENVIRONMENT"] = env.upper()  # pylint: disable=no-member
    load_dotenv()

    discord_token_key = f"DISCORD_BOT_TOKEN_{env.upper()}"  # pylint: disable=no-member
    discord_token = os.getenv(discord_token_key)

    if not discord_token:
        raise RuntimeError(f"Discord token not found in environment variable {discord_token_key}")

    os.environ["DISCORD_TOKEN"] = discord_token

    docker_up = subprocess.run(["docker", "compose", "up"], check=True)

    if not docker_up.returncode == 0:
        raise RuntimeError("Docker compose up failed")

@cli.command()
@click.option("-name", required=True, help="🛠️ Generate a new migration with the given name")
def migrate(name: str) -> None:  # pylint: disable=no-self-argument,no-method-argument
    generate_migration = subprocess.run(
        ["docker", "exec", "eggsauce_bot", "aerich", "migrate", "--name", name], check=True
    )

    if not generate_migration.returncode == 0:
        raise RuntimeError("Failed to generate migration")

    click.echo("Migration generated successfully")

    apply_migration = subprocess.run(["docker", "exec", "eggsauce_bot", "aerich", "upgrade"], check=True)

    if not apply_migration.returncode == 0:
        raise RuntimeError("Failed to apply migration")

    click.echo("Migration applied successfully")


@cli.command()
def apply_migrations() -> None:
    apply_migration = subprocess.run(["docker", "exec", "eggsauce_bot", "aerich", "upgrade"], check=True)

    if not apply_migration.returncode == 0:
        raise RuntimeError("Failed to apply migration")

    click.echo("Migration applied successfully")


@cli.command()
def build() -> None:  # pylint: disable=no-self-argument,no-method-argument
    docker_build = subprocess.run(["docker", "compose", "build"], check=True)

    if docker_build.returncode == 0:
        click.echo("Docker build successful")
    else:
        raise RuntimeError("Docker build failed")
