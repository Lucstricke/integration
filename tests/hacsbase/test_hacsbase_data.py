"""Data Test Suite."""
import pytest
from custom_components.hacs.base import HacsRepositories

from custom_components.hacs.hacsbase.data import HacsData

from tests.async_mock import patch


@pytest.mark.asyncio
async def test_hacs_data_async_write1(hacs, repository):
    data = HacsData()
    repository.data.installed = True
    repository.data.installed_version = "1"
    hacs.repositories.register(repository)
    await data.async_write()


@pytest.mark.asyncio
async def test_hacs_data_async_write2(hacs):
    data = HacsData()
    hacs.status.background_task = False
    hacs.system.disabled_reason = None
    hacs.repositories = HacsRepositories()
    await data.async_write()


@pytest.mark.asyncio
async def test_hacs_data_restore_write_new(hacs):
    data = HacsData()
    await data.restore()
    with patch(
        "custom_components.hacs.hacsbase.data.async_save_to_store"
    ) as mock_async_save_to_store, patch(
        "custom_components.hacs.hacsbase.data.async_save_to_store_default_encoder"
    ):
        await data.async_write()
    assert mock_async_save_to_store.called


@pytest.mark.asyncio
async def test_hacs_data_restore_write_not_new(hacs):
    data = HacsData()

    async def _mocked_loads(hass, key):
        if key == "repositories":
            return {
                "172733314": {
                    "category": "integration",
                    "full_name": "hacs/integration",
                    "installed": True,
                },
                "202226247": {
                    "category": "integration",
                    "full_name": "shbatm/hacs-isy994",
                    "installed": False,
                },
            }
        elif key == "hacs":
            return {"view": "Grid", "compact": False, "onboarding_done": True}
        elif key == "renamed_repositories":
            return {}
        else:
            raise ValueError(f"No mock for {key}")

    def _mocked_load(*_):
        return {
            "category": "integration",
            "show_beta": True,
        }

    with patch("os.path.exists", return_value=True), patch(
        "custom_components.hacs.hacsbase.data.async_load_from_store",
        side_effect=_mocked_loads,
    ), patch(
        "custom_components.hacs.helpers.functions.store.HACSStore.load",
        side_effect=_mocked_load,
    ):
        await data.restore()

    assert hacs.repositories.get_by_id("202226247")
    assert hacs.repositories.get_by_full_name("shbatm/hacs-isy994")

    assert hacs.repositories.get_by_id("172733314")
    assert hacs.repositories.get_by_full_name("hacs/integration")

    assert hacs.repositories.get_by_id("172733314").data.show_beta is True
    assert hacs.repositories.get_by_id("172733314").data.installed is True

    assert hacs.repositories.get_by_id("202226247").data.show_beta is True
    assert hacs.repositories.get_by_id("202226247").data.installed is True

    with patch(
        "custom_components.hacs.hacsbase.data.async_save_to_store"
    ) as mock_async_save_to_store, patch(
        "custom_components.hacs.hacsbase.data.async_save_to_store_default_encoder"
    ) as mock_async_save_to_store_default_encoder:
        await data.async_write()
    assert mock_async_save_to_store.called
    assert mock_async_save_to_store_default_encoder.called
