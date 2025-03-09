from discord import Embed
from discord.ext.commands import MinimalHelpCommand

__all__ = ("HelpCommandUsecase",)


class HelpCommandUsecase(MinimalHelpCommand):

    async def send_pages(self):
        destination = self.get_destination()

        for page in self.paginator.pages:
            embed = Embed(description=page)
            await destination.send(embed=embed)

    async def send_bot_help(self, mapping, /):
        embed = Embed(title="📚 Categories")
        embed.description = "Use `help <command>` for more info on a command."
        embed.description += "\nYou can also use `$help [category]` for more info on a category."
        cog_description = []

        for cog in mapping:
            if cog is None:
                continue

            if cog.qualified_name == "Developer":
                continue

            cog_description.append(
                f"`{cog.qualified_name}`: {cog.description if cog.description else 'No description'}"
            )

        embed.add_field(name="📜 Categories", value="\n".join(cog_description), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command, /):
        embed = Embed(title=f"ℹ️ Help with `{command.qualified_name}`")
        embed.add_field(name="📝 Description", value=command.help, inline=False)

        embed.add_field(name="🔧 Usage", value=self.get_command_signature(command), inline=False)

        if command.params:
            params_description = []

            for param_name, param in command.params.items():

                if param_name in ["self", "ctx"]:
                    continue

                params_description.append(
                    f"`{param_name}`: { param.description if param.description else 'No description'}"
                )

            if params_description:
                embed.add_field(name="📌 Parameters", value="\n".join(params_description), inline=False)

        if command.aliases:
            embed.add_field(name="🔗 Aliases", value=", ".join(command.aliases), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error, /):
        embed = Embed(title="❌ Something went wrong!", description=error)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog, /):
        embed = Embed(
            title=f"ℹ️ Help with `{cog.qualified_name}` Commands",
            description="Type `help <command>` for more info on a command.",
        )
        command_description = []

        for command in cog.get_commands():

            if command.hidden:
                continue

            command_description.append(f"`{self.context.clean_prefix}{command.name}: {command.signature}`")

        embed.add_field(name="📜 Commands", value="\n".join(command_description), inline=False)
        await self.get_destination().send(embed=embed)
