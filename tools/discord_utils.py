from typing import Union, Optional
from discord import Member
from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from discord import Interaction, Embed, Forbidden, ButtonStyle
from discord.ui import View, Button
from .constants import REASON_DM_FAILURE

__all__ = [
    "send_bot_embed",
    "embed_builder",
    "send_user_dm",
    "send_failed_embed",
    "button_builder",
    "view_button_builder",
    "confirmation_popup",
    "extract_discord_user",
]


async def send_bot_embed(
    ctx: Context[BotT] | Interaction,
    color: str = "#FEE75C",
    footer_text: Optional[str] = None,
    ephemeral: bool = False,
    thumbnail_url: Optional[str] = None,
    view: Optional[View] = None,
    **kwargs
) -> None:
    """This function is responsable for sending an embed for the user.

    Args:
        ctx (Union[Context, Interaction]): The context of the command.
        color (str, optional): The color of the embed, defaults to "#FEE75C".
        footer_text (Optional[str], optional): The text that will be displayed in the footer of the embed.
        Defaults to None.
        ephemeral (bool, optional): A boolean that checks if the message should be sent privately within the server.
        Defaults to False.
        embed_file (Optional[str], optional): The file that will be sent with the embed. Defaults to None.
        thumbnail_url (Optional[str], optional): The URL of the thumbnail that will be displayed in the embed.
        Defaults to None.
        view (Optional[View], optional): The view that will be sent with the embed. Defaults to None.

    Raises:
        ValueError: If ephemeral and is_dm are both True or if ephemeral is True and the context is not an interaction.
    """
    embed = embed_builder(color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs)

    if isinstance(ctx, Interaction):
        await _handle_interaction_respose(ctx, embed, ephemeral, view)
        return

    if ctx.interaction is not None:
        await _handle_interaction_respose(ctx.interaction, embed, ephemeral, view)
        return

    if view is not None:
        await ctx.send(embed=embed, ephemeral=ephemeral, view=view)
    else:
        await ctx.send(embed=embed, ephemeral=ephemeral)


async def _handle_interaction_respose(
    interaction: Interaction, embed: Embed, ephemeral: bool, view: Optional[View]
) -> None:
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
    footer_text: Optional[str] = None, thumbnail_url: Optional[str] = None, color: str = "#FEE75C", **kwargs
) -> Embed:
    """This function is responsable for building the embed that will be sent to the user.

    Args:
        ctx (Union[Context, Interaction]): The context of the command.
        color (str): The color of the embed in hexadecimal.
        footer_text (Optional[str]): The text that will be displayed in the footer of the embed.

    Returns:
        discord.Embed: The embed that will be sent to the user.
    """
    embed = Embed(color=int(color.replace("#", ""), 16), **kwargs)

    if footer_text:
        embed.set_footer(text=footer_text)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    return embed


async def send_user_dm(ctx: Context[BotT] | Interaction, embed: Embed) -> None:
    """This function is responsable for sending a message to the user's DM.

    Args:
        ctx (Union[Context, Interaction]): The context of the command.
        embed (Embed): The embed that will be sent to the user.
    """

    try:
        if isinstance(ctx, Interaction):
            await ctx.user.send(embed=embed)

        elif ctx.interaction:
            await ctx.interaction.user.send(embed=embed)

        else:
            await ctx.author.send(embed=embed)
    except Forbidden:
        await send_bot_embed(
            ctx,
            title="Error",
            description=REASON_DM_FAILURE,
            color="#FF0000",
        )
        return


async def send_failed_embed(ctx: Union[Context[BotT], Interaction], description: str, ephemeral: bool = True) -> None:
    """This function is responsable for sending an embed when a command fails.
    This works the same as the `send_bot_embed` coroutine, but with a predefined title.

    Args:
        context (Context): The context of the command.
        description (str): The description of the embed.
    """
    return await send_bot_embed(
        ctx=ctx,
        ephemeral=ephemeral,
        title="❌ Command failed",
        description=description,
    )


def button_builder(**kwargs) -> Button:
    """
    Function that creates a button.

    Args:
        **kwargs: The keyword arguments that will be passed to the button builder.

    Returns:
        Button: The button.
    """
    return Button(**kwargs)


def view_button_builder(*buttons) -> View:
    """
    Function that creates a view with buttons.

    Args:
        *buttons: The buttons that will be added to the view.

    Returns:
        View: The view.
    """
    view = View()
    for button in buttons:
        if not isinstance(button, Button):
            raise TypeError("All buttons must be of type Button.")
        view.add_item(button)
    return view


async def confirmation_popup(
    ctx: Context[BotT] | Interaction,
    description: str,
    title: str = "🔔 Please Confirm Your Action",
    ephemeral=True,
) -> bool:
    """
    Function that creates a confirmation popup.

    Args:
        ctx (Context): The context of the command.
        embed (Embed): The embed that will be sent.
        ephemeral (bool): Whether the message should be ephemeral or not.
        is_dm (bool): Whether the message should be sent in DMs or not.
    """
    cancel_button = button_builder(label="Cancel", style=ButtonStyle.red, custom_id="cancel")
    confirm_button = button_builder(label="Confirm", style=ButtonStyle.green, custom_id="confirm")

    view = view_button_builder(cancel_button, confirm_button)

    await send_bot_embed(ctx, ephemeral=ephemeral, view=view, description=description, title=title)

    if isinstance(ctx, Interaction):
        client = ctx.client
        author = ctx.user
    elif ctx.interaction:
        client = ctx.interaction.client
        author = ctx.interaction.user
    else:
        client = ctx.bot
        author = ctx.author

    try:
        interaction = await client.wait_for("interaction", check=lambda i: i.user.id == author.id, timeout=60)
        await interaction.response.defer(ephemeral=ephemeral)
        if interaction.data["custom_id"] == "confirm":  # type: ignore
            return True
        return False
    except TimeoutError:
        return False
    
def extract_discord_user(author: Member, mentioned_user: Optional[Member]) -> Member:
    """Extracts the discord user from the command.

    Args:
        author (Member): The author of the command.
        possible_mentioned_user (Member): The possible mentioned user.

    Returns:
        Member: The discord user.
    """
    if mentioned_user:
        return mentioned_user
    return author
