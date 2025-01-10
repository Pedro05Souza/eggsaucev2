from typing import Union, Optional
from discord.ext.commands import Context
from discord import Interaction, Color, Embed, Forbidden, ButtonStyle
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
]


async def send_bot_embed(
    ctx: Union[Context, Interaction],
    color: str = "#FEE75C",
    footer_text: Optional[str] = None,
    ephemeral: bool = False,
    is_dm: bool = False,
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
        is_dm (bool, optional): Checks if the message should be sent privately to the user.
        Defaults to False.
        embed_file (Optional[str], optional): The file that will be sent with the embed. Defaults to None.
        thumbnail_url (Optional[str], optional): The URL of the thumbnail that will be displayed in the embed.
        Defaults to None.
        view (Optional[View], optional): The view that will be sent with the embed. Defaults to None.

    Raises:
        ValueError: If ephemeral and is_dm are both True or if ephemeral is True and the context is not an interaction.
    """
    if ephemeral and is_dm:
        raise ValueError("Cannot have both ephemeral and is_dm as True")

    is_interaction = hasattr(ctx, "interaction") and ctx.interaction is not None

    if is_interaction:
        if not ctx.interaction.response.is_done():
            return await ctx.interaction.response.send_message(
                embed=embed_builder(color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs),
                ephemeral=ephemeral,
                view=view,
            )

        return await ctx.interaction.followup.send(
            embed=embed_builder(color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs),
            ephemeral=ephemeral,
            view=view,
        )

    return await ctx.send(
        embed=embed_builder(color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs), view=view
    )


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


async def send_user_dm(ctx: Union[Context, Interaction], embed: Embed) -> None:
    """This function is responsable for sending a message to the user's DM.

    Args:
        ctx (Union[Context, Interaction]): The context of the command.
        embed (Embed): The embed that will be sent to the user.
    """
    is_interaction = isinstance(ctx, Interaction)

    try:
        if is_interaction:
            await ctx.user.send(embed=embed)
        else:
            await ctx.author.send(embed=embed)
    except Forbidden:
        await send_bot_embed(
            ctx,
            title="Error",
            description=REASON_DM_FAILURE,
            color=Color.red(),
            ephemeral=True,
        )
        return


async def send_failed_embed(ctx: Union[Context, Interaction], description: str, ephemeral: bool = True) -> None:
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
    ctx: Context | Interaction,
    description: str,
    title: str = "🔔 Please Confirm Your Action",
    ephemeral=True,
    is_dm=False,
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

    is_interaction = isinstance(ctx, Interaction)

    await send_bot_embed(ctx, ephemeral=ephemeral, is_dm=is_dm, view=view, description=description, title=title)

    client = ctx.client if is_interaction else ctx.bot  # Interaction and Context have different names for the bot.
    author = ctx.user if is_interaction else ctx.author  # Interaction and Context have different names for the author.

    try:
        interaction = await client.wait_for("interaction", check=lambda i: i.user.id == author.id, timeout=60)
        await interaction.response.defer()

        if interaction.data["custom_id"] == "confirm":
            return True
        return False
    except TimeoutError:
        return False
