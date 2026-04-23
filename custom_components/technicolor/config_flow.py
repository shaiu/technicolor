"""Config flow to configure the Technicolor integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from .const import CONF_USE_SSL, CONF_VERIFY_SSL, DOMAIN
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import callback

RESULT_UNKNOWN = "unknown"
RESULT_SUCCESS = "success"

_LOGGER = logging.getLogger(__name__)


class TechnicolorFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize Technicolor config flow."""
        self._host = None

    @callback
    def _show_setup_form(self, user_input=None, errors=None):
        """Show the setup form to the user."""

        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
                    vol.Optional(CONF_PORT, default=user_input.get(CONF_PORT, 80)): int,
                    vol.Optional(CONF_USE_SSL, default=user_input.get(CONF_USE_SSL, False)): bool,
                    vol.Optional(
                        CONF_VERIFY_SSL, default=user_input.get(CONF_VERIFY_SSL, True)
                    ): bool,
                    vol.Required(CONF_USERNAME, default=user_input.get(CONF_USERNAME, "")): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is None:
            return self._show_setup_form(user_input)

        self._host = user_input[CONF_HOST]
        await self.async_set_unique_id(self._host)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._host,
            data=user_input,
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry."""
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "TechnicolorOptionsFlowHandler":
        return TechnicolorOptionsFlowHandler()


def _config_schema_defaults(entry: config_entries.ConfigEntry) -> dict:
    merged = {**entry.data, **entry.options}
    return {
        CONF_PORT: merged.get(CONF_PORT, 80),
        CONF_USE_SSL: merged.get(CONF_USE_SSL, False),
        CONF_VERIFY_SSL: merged.get(CONF_VERIFY_SSL, True),
    }


class TechnicolorOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow to change port / SSL for an existing config entry."""

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        defaults = _config_schema_defaults(self.config_entry)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PORT, default=defaults[CONF_PORT]): int,
                    vol.Optional(CONF_USE_SSL, default=defaults[CONF_USE_SSL]): bool,
                    vol.Optional(CONF_VERIFY_SSL, default=defaults[CONF_VERIFY_SSL]): bool,
                }
            ),
        )
