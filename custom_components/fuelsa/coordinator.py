"""Shared price updates."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FuelSAAuthError, FuelSAClient, FuelSAError, FuelPrice
from .const import DOMAIN


class FuelSACoordinator(DataUpdateCoordinator[dict[str, FuelPrice]]):
    """Fetch all grades and regions in one request."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: FuelSAClient) -> None:
        super().__init__(hass, logging.getLogger(__name__), name=DOMAIN,
                         config_entry=entry, update_interval=timedelta(hours=6),
                         always_update=False)
        self.client = client

    async def _async_update_data(self) -> dict[str, FuelPrice]:
        try:
            return await self.client.async_get_prices()
        except FuelSAAuthError as err:
            raise ConfigEntryAuthFailed("Fuel SA API key rejected") from err
        except FuelSAError as err:
            raise UpdateFailed(str(err)) from err
