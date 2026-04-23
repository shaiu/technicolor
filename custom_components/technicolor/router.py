import logging
from datetime import timedelta
import asyncio

from technicolorgateway import TechnicolorGateway

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from .const import CONF_USE_SSL, CONF_VERIFY_SSL, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class TechnicolorRouter:
    """Representation of a Technicolor router."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize a Technicolor router."""
        self.hass = hass
        self.loop = asyncio.get_running_loop()
        self._entry = entry
        self._host = entry.data[CONF_HOST]
        self._user = entry.data[CONF_USERNAME]
        self._pass = entry.data[CONF_PASSWORD]
        self._port = int(self._get_entry_value(entry, CONF_PORT, 80))
        self._use_ssl = bool(self._get_entry_value(entry, CONF_USE_SSL, False))
        self._verify_ssl = bool(self._get_entry_value(entry, CONF_VERIFY_SSL, True))

        self._api: TechnicolorGateway = None
        self._unsub_update = None

        self.devices = {}

        self.listeners = []

    @property
    def entry_id(self) -> str:
        return self._entry.entry_id

    @property
    def host(self) -> str:
        return self._host

    @staticmethod
    def _get_entry_value(entry: ConfigEntry, key: str, default):
        if key in entry.options:
            return entry.options[key]
        return entry.data.get(key, default)

    async def setup(self) -> None:
        self._api = TechnicolorGateway(
            self._host, str(self._port), self._user, self._pass
        )
        scheme = "https" if self._use_ssl else "http"
        self._api._uri = f"{scheme}://{self._host}:{self._port}"
        if self._use_ssl and not self._verify_ssl:
            self._api._br.session.verify = False

        try:
            await self.loop.run_in_executor(None, self._api.authenticate)
        except Exception:
            _LOGGER.exception("Failed to connect to Technicolor")
            raise ConfigEntryNotReady

        await self.update_all(None)

        self._unsub_update = async_track_time_interval(
            self.hass, self.update_all, SCAN_INTERVAL
        )

    def async_unload(self) -> None:
        if self._unsub_update is not None:
            self._unsub_update()
            self._unsub_update = None

    async def update_all(self, now) -> None:
        """Update all Technicolor platforms."""
        _LOGGER.debug("update_all")
        await self.update_device_trackers()

    async def update_device_trackers(self) -> None:
        _LOGGER.debug("update_device_trackers")
        new_device = None
        devices = await self.loop.run_in_executor(None, self._api.get_device_modal)
        _LOGGER.debug("update_device_trackers devices %s", devices)

        for device in devices:
            device_mac = device["mac"]
            _LOGGER.debug("device: %s", device_mac)
            if self.devices.get(device_mac) is None:
                new_device = True
                _LOGGER.debug("new")

            self.devices[device_mac] = device

        async_dispatcher_send(self.hass, self.signal_device_update)

        if new_device:
            async_dispatcher_send(self.hass, self.signal_device_new)

    @property
    def signal_device_update(self) -> str:
        """Event specific per Technicolor entry to signal updates in devices."""
        return f"{DOMAIN}-{self.entry_id}-device-update"

    @property
    def signal_device_new(self) -> str:
        """Event specific per Technicolor entry to signal new device."""
        return f"{DOMAIN}-{self.entry_id}-device-new"
