"""Home Assistant integration for South African fuel prices."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FuelSAClient
from .coordinator import FuelSACoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Validate the initial fetch before loading entities."""
    coordinator = FuelSACoordinator(
        hass, entry, FuelSAClient(async_get_clientsession(hass), entry.data[CONF_API_KEY])
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload sensors and their update listeners."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
