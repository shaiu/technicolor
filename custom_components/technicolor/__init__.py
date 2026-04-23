"""The technicolor integration."""
from datetime import timedelta

from .const import DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .router import TechnicolorRouter

PLATFORMS = [Platform.DEVICE_TRACKER]
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup(hass, config):
    """Set up the technicolor integration."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    # save the options from config yaml
    options = {}
    hass.data[DOMAIN] = {"yaml_options": options}

    # Support importing one or multiple routers from YAML.
    conf_list = conf if isinstance(conf, list) else [conf]
    for router_conf in conf_list:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=router_conf
            )
        )

    return True


async def _async_config_entry_update(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Technicolor platform."""

    # import options from yaml if empty
    yaml_options = hass.data.get(DOMAIN, {}).pop("yaml_options", {})
    if not entry.options and yaml_options:
        hass.config_entries.async_update_entry(entry, options=yaml_options)

    entry.async_on_unload(entry.add_update_listener(_async_config_entry_update))

    technicolor_router = TechnicolorRouter(hass, entry)
    await technicolor_router.setup()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DOMAIN: technicolor_router,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        router = hass.data[DOMAIN].pop(entry.entry_id, {}).get(DOMAIN)
        if router:
            router.async_unload()
    return unload_ok
