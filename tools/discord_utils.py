from typing import Union, Optional
from discord.ext.commands import Context
from discord import Interaction, Color, Embed, Forbidden
from .error_reasons import REASON_DM_FAILURE

__all__ = ["send_bot_embed", "embed_builder", "send_user_dm"]


async def send_bot_embed(
    ctx: Union[Context, Interaction],
    color: str = "#FEE75C",
    footer_text: Optional[str] = None,
    ephemeral: bool = False,
    is_dm: bool = False,
    thumbnail_url: Optional[str] = None,
    **kwargs
) -> None:
    """This function is responsable for sending an embed for the user.

    Args:
        ctx (Union[Context, Interaction]): The context of the command.
        color (str, optional): The color of the embed, defaults to "#FEE75C".
        footer_text (Optional[str], optional): The text that will be displayed in the footer of the embed. Defaults to None.
        ephemeral (bool, optional): A boolean that checks if the message should be sent privately within the server. Defaults to False.
        is_dm (bool, optional): Checks if the message should be sent privately to the user. Defaults to False.
        embed_file (Optional[str], optional): The file that will be sent with the embed. Defaults to None.
        thumbnail_url (Optional[str], optional): The URL of the thumbnail that will be displayed in the embed. Defaults to None.

    Raises:
        ValueError: If ephemeral and is_dm are both True or if ephemeral is True and the context is not an interaction.
    """
    if ephemeral and is_dm:
        raise ValueError("Cannot have both ephemeral and is_dm as True")

    is_interaction = isinstance(ctx, Interaction)

    if ephemeral and not is_interaction:
        raise ValueError("Ephemeral can only be used with interactions")
    
    if is_interaction:
        if not ctx.response.is_done():
            return await ctx.response.send_message(
                embed=await embed_builder(
                    color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs
                ),
                ephemeral=ephemeral,
            )

        return await ctx.followup.send(
            embed=await embed_builder(color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs),
            ephemeral=ephemeral,
        )

    return await ctx.send(
        embed=await embed_builder(color=color, footer_text=footer_text, thumbnail_url=thumbnail_url, **kwargs),
    )


async def embed_builder(
    color: str,
    footer_text: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    **kwargs
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
