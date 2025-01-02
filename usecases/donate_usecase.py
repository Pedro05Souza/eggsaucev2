from typing import Union
from discord import Member, Interaction
from discord.ext.commands import Context
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from repositories import PlayerRepository
from tools import REASON_INVALID_USER, REASON_INVALID_AMOUNT, send_bot_embed

class DonateUsecase:

    def __init__(
        self,
        context: Union[Context, Interaction],
        donator: PlayerEntity,
        donation_amount: int,
        recipient: Member,
        player_repository: PlayerRepository,
    ) -> None:
        self.context = context
        self.donator = donator
        self.donation_amount = donation_amount
        self.recipient = recipient
        self.player_repository = player_repository

    async def donate(self) -> None:
        recipient_entity = await self.player_repository.get_player_by_discord_id(self.recipient.id)
        
        if not recipient_entity or recipient_entity.id == self.donator.id:
            return await send_bot_embed(
                ctx=self.context,
                title="❌ Donation failed",
                description=REASON_INVALID_USER,
                thumbnail_url=self.context.author.display_avatar.url
            )
            
        if self.donation_amount <= 0:
            return await send_bot_embed(
                ctx=self.context,
                title="❌ Donation failed",
                description=REASON_INVALID_AMOUNT,
                thumbnail_url=self.context.author.display_avatar.url
            )
        
        self.donator.balance -= self.donation_amount
        recipient_entity.balance += self.donation_amount
        
        async with in_transaction():
            await self.player_repository.update_player(self.donator)
            await self.player_repository.update_player(recipient_entity)
            return await send_bot_embed(
                ctx=self.context,
                title="✅ Donation successful",
                description=f"You donated {self.donation_amount} eggbux to {self.recipient.mention}",
            )
