import pytest
from usecases import SetPrefixUsecase


class TestSetPrefixUsecase:

    @pytest.mark.asyncio
    async def test_set_prefix(self, ctx, bot_config_cache_service, bot_config_repository):
        set_prefix_usecase = SetPrefixUsecase(ctx, bot_config_cache_service, bot_config_repository, "!")

        await set_prefix_usecase.set_prefix()

        bot_config_repository.update_bot_config.assert_called_once()
