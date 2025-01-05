import subprocess
import os
import click
from dotenv import load_dotenv


class BotManager:

    @click.group()
    def cli():  # pylint: disable=no-self-argument,no-method-argument
        pass

    @cli.command()
    @click.option("--env", type=click.Choice(["dev", "prod"]), default="dev")
    def run(env):  # pylint: disable=no-self-argument,no-method-argument
        os.environ["ENVIRONMENT"] = env.upper()  # pylint: disable=no-member
        load_dotenv()

        discord_token_key = f"DISCORD_BOT_TOKEN_{env.upper()}"  # pylint: disable=no-member
        discord_token = os.getenv(discord_token_key)

        if not discord_token:
            raise RuntimeError(f"Discord token not found in environment variable {discord_token_key}")

        os.environ["DISCORD_TOKEN"] = discord_token

        docker_up = subprocess.run(["docker", "compose", "up"], check=True)

        if docker_up.returncode == 0:
            click.echo("Docker compose up successful")
        else:
            raise RuntimeError("Docker build failed")

    @cli.command()
    def build():  # pylint: disable=no-self-argument,no-method-argument
        docker_build = subprocess.run(["docker", "compose", "build"], check=True)

        if docker_build.returncode == 0:
            click.echo("Docker build successful")
        else:
            raise RuntimeError("Docker build failed")
