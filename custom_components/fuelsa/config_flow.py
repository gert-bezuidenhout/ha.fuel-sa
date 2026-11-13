"""UI setup and API key reauthentication."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import FuelSAAuthError, FuelSAClient, FuelSAError
from .const import DOMAIN

SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): TextSelector(
    TextSelectorConfig(type=TextSelectorType.PASSWORD))})


class FuelSAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """One national price feed per Home Assistant instance."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._async_credentials("user", user_input)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._async_credentials("reauth_confirm", user_input)

    async def _async_credentials(self, step_id, user_input):
        errors = {}
        if step_id == "user":
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            try:
                if not api_key:
                    raise FuelSAAuthError("Empty key")
                await FuelSAClient(async_get_clientsession(self.hass), api_key).async_get_prices()
            except FuelSAAuthError:
                errors["base"] = "invalid_auth"
            except FuelSAError:
                errors["base"] = "cannot_connect"
            else:
                data = {CONF_API_KEY: api_key}
                if step_id == "reauth_confirm":
                    return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=data)
                return self.async_create_entry(title="Fuel SA", data=data)
        return self.async_show_form(step_id=step_id, data_schema=SCHEMA, errors=errors)
