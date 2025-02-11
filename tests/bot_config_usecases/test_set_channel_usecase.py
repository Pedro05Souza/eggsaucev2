import pytest
from usecases import SetChannelUsecase


class TestSetChannelUsecase:

    @pytest.mark.asyncio
    async def test_if_channel_is_already_set(
        self, ctx, bot_config_entity, bot_config_cache_service, bot_config_repository
    ) -> None:
        bot_config_entity.allowed_channels.add(123)
        ctx.entities.bot_config_entity = bot_config_entity

        set_channel_usecase = SetChannelUsecase(ctx, 123, bot_config_cache_service, bot_config_repository)

        await set_channel_usecase.set_channel()

        bot_config_repository.create_allowed_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_if_channel_was_created(
        self, ctx, bot_config_entity, bot_config_cache_service, bot_config_repository
    ) -> None:
        ctx.entities.bot_config_entity = bot_config_entity

        set_channel_usecase = SetChannelUsecase(ctx, 123, bot_config_cache_service, bot_config_repository)

        await set_channel_usecase.set_channel()

        bot_config_repository.create_allowed_channel.assert_called_once_with(bot_config_entity.id, 123)

    @pytest.mark.asyncio
    async def test_database_failure(
        self, ctx, bot_config_entity, bot_config_cache_service, bot_config_repository
    ) -> None:
        ctx.entities.bot_config_entity = bot_config_entity
        bot_config_cache_service.add_item(bot_config_entity.guild_id, bot_config_entity)
        bot_config_repository.create_allowed_channel.side_effect = Exception()

        set_channel_usecase = SetChannelUsecase(ctx, 123, bot_config_cache_service, bot_config_repository)

        with pytest.raises(Exception):
            await set_channel_usecase.set_channel()
            bot_config_cache_service.remove_if_exception.assert_called_once_with(bot_config_entity.guild_id)
            assert bot_config_cache_service.get_item(bot_config_entity.guild_id) is None
