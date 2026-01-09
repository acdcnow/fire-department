"""The TimeTree integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import DOMAIN, CONF_CALENDAR_ID
from .api import TimeTreeApi
from .coordinator import TimeTreeCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["calendar", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TimeTree from a config entry."""
    _LOGGER.debug("Setting up TimeTree integration for: %s", entry.title)
    
    hass.data.setdefault(DOMAIN, {})

    try:
        email = entry.data[CONF_EMAIL]
        password = entry.data[CONF_PASSWORD]
        calendar_id = entry.data[CONF_CALENDAR_ID]

        _LOGGER.debug("Initializing API for user: %s", email)
        api = TimeTreeApi(hass, email, password)
        
        _LOGGER.debug("Initializing Coordinator for calendar ID: %s", calendar_id)
        coordinator = TimeTreeCoordinator(hass, api, calendar_id, entry)
        
        # Fetch initial data
        _LOGGER.debug("Requesting initial data refresh...")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("Initial data refresh successful.")

        hass.data[DOMAIN][entry.entry_id] = coordinator

        _LOGGER.debug("Forwarding setup to platforms: %s", PLATFORMS)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.debug("Platform setup forwarded.")

        # Register update listener
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        return True
    
    except Exception as e:
        _LOGGER.exception("Error setting up TimeTree integration: %s", e)
        return False

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry when options change."""
    _LOGGER.debug("Reloading TimeTree entry for: %s", entry.title)
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading TimeTree entry for: %s", entry.title)
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
