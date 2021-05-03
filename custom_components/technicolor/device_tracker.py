"""Support for Technicolor routers."""
import logging
from typing import Dict, Any

import voluptuous as vol
from technicolorgateway import TechnicolorGateway

import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICES,
    CONF_EXCLUDE,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback

DOMAIN = "technicolor"
DEFAULT_DEVICE_NAME = "Unknown device"
SOURCE_TYPE_ROUTER = "router"

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_DEVICES, default=[]): vol.All(cv.ensure_list, [cv.string]),
                vol.Optional(CONF_EXCLUDE, default=[]): vol.All(cv.ensure_list, [cv.string]),
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up device tracker for Technicolor component."""
    gateway = hass.data[DOMAIN][entry.entry_id][DOMAIN]

    tracked = set()

    @callback
    def update_gateway():
        """Update the values of the router."""
        add_entities(gateway, async_add_entities, tracked)

    update_gateway()




@callback
def add_entities(gateway, async_add_entities, tracked):
    """Add new tracker entities from the gateway."""
    new_tracked = []

    devices = gateway.get_device_modal()

    for device in devices:
        mac = device['mac']
        if mac in tracked:
            continue

        new_tracked.append(TechnicolorDeviceScanner(gateway, device))
        tracked.add(mac)

    if new_tracked:
        async_add_entities(new_tracked)


class TechnicolorDeviceScanner(ScannerEntity):
    """Representation of a Technicolor device."""

    def __init__(self, gateway: TechnicolorGateway, device) -> None:
        """Initialize a AsusWrt device."""
        self._gateway = gateway
        self._device = device

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._device['mac']

    @property
    def name(self) -> str:
        """Return the name."""
        return self._device['name'] or DEFAULT_DEVICE_NAME

    @property
    def is_connected(self):
        """Return true if the device is connected to the network."""
        return True

    @property
    def source_type(self) -> str:
        """Return the source type."""
        return SOURCE_TYPE_ROUTER

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the attributes."""
        return {}

    @property
    def hostname(self) -> str:
        """Return the hostname of device."""
        return self._device['name']

    @property
    def ip_address(self) -> str:
        """Return the primary ip address of the device."""
        return self._device['ip']

    @property
    def mac_address(self) -> str:
        """Return the mac address of the device."""
        return self._device['mac']

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device information."""
        return {}

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False
