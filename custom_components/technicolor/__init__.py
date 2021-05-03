"""The technicolor integration."""

from .const import DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from technicolorgateway import TechnicolorGateway

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant


async def async_setup(hass, config):
    """Set up the technicolor integration."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    # save the options from config yaml
    options = {}
    hass.data[DOMAIN] = {"yaml_options": options}

    # check if already configured
    domains_list = hass.config_entries.async_domains()
    if DOMAIN in domains_list:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Technicolor platform."""

    # import options from yaml if empty
    yaml_options = hass.data.get(DOMAIN, {}).pop("yaml_options", {})
    if not entry.options and yaml_options:
        hass.config_entries.async_update_entry(entry, options=yaml_options)

    gateway = TechnicolorGateway(
        entry.data[CONF_HOST], "80", entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )
    gateway.srp6authenticate()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DOMAIN: gateway,
    }

    return True
