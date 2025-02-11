import pytest
from usecases import UnsetChannelUsecase


class TestUnsetChannelUseCase:

    @pytest.mark.asyncio
    async def test_unset_channel_usecase(self, ctx, bot_config_cache_service, bot_config_repository, bot_config_entity):
        bot_config_entity.allowed_channels.add(123)
        ctx.entities.bot_config_entity = bot_config_entity
        unset_channel_usecase = UnsetChannelUsecase(ctx, 123, bot_config_cache_service, bot_config_repository)

        await unset_channel_usecase.unset_channel()

        bot_config_repository.delete_allowed_channel.assert_called_once_with(bot_config_entity.id, 123)

    @pytest.mark.asyncio
    async def test_unset_channel_usecase_not_present(
        self, ctx, bot_config_cache_service, bot_config_repository, bot_config_entity
    ):
        ctx.entities.bot_config_entity = bot_config_entity
        unset_channel_usecase = UnsetChannelUsecase(ctx, 123, bot_config_cache_service, bot_config_repository)

        await unset_channel_usecase.unset_channel()

        bot_config_repository.delete_allowed_channel.assert_not_called()
