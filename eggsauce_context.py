from __future__ import annotations
from typing import Optional, Any, TypedDict
from datetime import datetime
from discord import Embed, Colour
from discord.types.embed import EmbedType
from discord import Forbidden, Interaction, ButtonStyle, Member
from discord.ui import View, button, Button
from discord.ext.commands import Context
from tools.constants import REASON_DM_FAILURE

__all__ = ["EggsauceContext"]


class _EmbedParams(TypedDict, total=False):
    title: Any | None
    type: EmbedType
    url: Any | None
    description: Any
    timestamp: datetime | None
    colour: int | Colour | None


class EggsauceContext(Context):

    async def send_bot_embed(
        self,
        embed_params: _EmbedParams,
        color: str = "#FEE75C",
        footer_text: Optional[str] = None,
        ephemeral: bool = False,
        thumbnail_url: Optional[str] = None,
        view: Optional[View] = None,
    ) -> None:
        """This function is responsable for sending an embed for the user.

        Args:
            ctx ([Context | Interaction]): The context of the command.
            embed_params (_EmbedParams): The parameters that will be passed to the embed builder.
            color (str, optional): The color of the embed, defaults to "#FEE75C".
            footer_text (Optional[str], optional): The text that will be displayed in the footer of the embed.
            Defaults to None.
            ephemeral (bool, optional): A boolean that checks if the message should be sent privately within the server.
            Defaults to False.
            thumbnail_url (Optional[str], optional): The URL of the thumbnail that will be displayed in the embed.
            Defaults to None.
            view (Optional[View], optional): The view that will be sent with the embed. Defaults to None.

        Raises:
            ValueError: If ephemeral and is_dm are both True
            or if ephemeral is True and the context is not an interaction.
        """
        embed = self.embed_builder(
            color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, embed_params=embed_params
        )

        if self.interaction is not None:
            await self.handle_interaction_response(self.interaction, embed, ephemeral, view)
            return

        if view is not None:
            await self.send(embed=embed, ephemeral=ephemeral, view=view)
        else:
            await self.send(embed=embed, ephemeral=ephemeral)

    async def handle_interaction_response(
        self, interaction: Interaction, embed: Embed | _EmbedParams, ephemeral: bool = True, view: Optional[View] = None
    ) -> None:

        if isinstance(embed, dict):
            embed = self.embed_builder(embed)

        if not interaction.response.is_done():
            if view is not None:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral, view=view)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            return

        if view is not None:
            await interaction.followup.send(embed=embed, ephemeral=ephemeral, view=view)
        else:
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)

    def embed_builder(
        self,
        embed_params: _EmbedParams,
        footer_text: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        color: str = "#FEE75C",
    ) -> Embed:
        """This function is responsable for building the embed that will be sent to the user.

        Args:
            embed_params (EmbedParams): The parameters that will be passed to the embed builder.
            footer_text (Optional[str]): The text that will be displayed in the footer of the embed.
            thumbnail_url (Optional[str]): The URL of the thumbnail that will be displayed in the embed.
            color (str, optional): The color of the embed, defaults to "#FEE75C".

        Returns:
            discord.Embed: The embed that will be sent to the user.
        """

        if not embed_params.get("type"):
            embed_params["type"] = "rich"

        embed = Embed(color=int(color.replace("#", ""), 16), **embed_params)

        if footer_text:
            embed.set_footer(text=footer_text)

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        return embed

    async def send_user_dm(self, embed: Embed) -> None:
        """This function is responsable for sending a message to the user's DM.

        Args:
            ctx Context | Interaction]: The context of the command.
            embed (Embed): The embed that will be sent to the user.
        """

        try:
            if isinstance(self, Interaction):
                await self.user.send(embed=embed)

            elif self.interaction:
                await self.interaction.user.send(embed=embed)

            else:
                await self.author.send(embed=embed)
        except Forbidden:
            await self.send_bot_embed(
                embed_params={
                    "title": "❌ Failed to send DM",
                    "description": REASON_DM_FAILURE,
                },
                color="#FF0000",
            )
            return

    async def handle_failed_interaction(
        self, interaction: Interaction, description: str, ephemeral: bool = True
    ) -> None:
        """This function is responsable for sending an embed when a command fails.

        Args:
            context (Context): The context of the command.
            embed (Embed): The embed that will be sent to the user.
            ephemeral (bool): Whether the message should be ephemeral or not.
        """
        embed = self.embed_builder(
            embed_params={
                "title": "❌ Command failed",
                "description": description,
            },
            color="#FF0000",
        )
        await self.handle_interaction_response(interaction, embed, ephemeral)

    async def send_failed_embed(self, description: str, ephemeral: bool = True) -> None:
        """This function is responsable for sending an embed when a command fails.
        This works the same as the `send_bot_embed` coroutine, but with a predefined title.

        Args:
            context (Context): The context of the command.
            description (str): The description of the embed.
            ephemeral (bool): Whether the message should be ephemeral or not.
        """
        return await self.send_bot_embed(
            ephemeral=ephemeral,
            embed_params={
                "title": "❌ Command failed",
                "description": description,
            },
        )

    async def confirmation_popup(
        self,
        description: str,
        title: str = "🔔 Please Confirm Your Action",
        member_to_confirm: Optional[Member] = None,
        ephemeral: bool = True,
    ):
        """This function is responsable for creating a confirmation popup.

        Args:
            ctx (Context | Interaction): The context of the command.
            description (str): The description of the embed.
            title (str): The title of the embed. Defaults to "🔔 Please Confirm Your Action".
            member_to_confirm (Optional[Member]): The member that will be asked to confirm the action. If no value
            is passed, the author of the command will be asked to confirm. Defaults to None.
            ephemeral (bool): Whether the message should be ephemeral or not.
        """
        confirmation_user = self.author

        if member_to_confirm:
            confirmation_user = member_to_confirm

        embed = Embed(title=title, description=description)
        confirmation_popup = _ConfirmationPopUp(
            embed,
            confirmation_user,  # type: ignore
            ephemeral,
        )
        message = await self.send(embed=embed, view=confirmation_popup)
        await confirmation_popup.wait()
        return confirmation_popup.value, message


class _ConfirmationPopUp(View):

    def __init__(
        self,
        embed: Embed,
        author: Member,
        ephemeral: bool = True,
    ) -> None:
        super().__init__(timeout=50)
        self.value = None
        self.embed = embed
        self.ephemeral = ephemeral
        self.author = author

    @button(label="Cancel", style=ButtonStyle.red, custom_id="cancel")
    async def cancel(self, interaction: Interaction, _: Button[View]):
        await interaction.response.defer()

        if interaction.user != self.author:
            return

        self.value = False
        self.stop()

    @button(label="Confirm", style=ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: Interaction, _: Button[View]):
        await interaction.response.defer()

        if interaction.user != self.author:
            return

        self.value = True
        self.stop()
