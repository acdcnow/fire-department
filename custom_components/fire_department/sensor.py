"""Platform for sensor integration."""
import logging
import aiohttp
import async_timeout
import re
from datetime import timedelta
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN, 
    CONF_PAGES, 
    CONF_UPDATE_INTERVAL, 
    DEFAULT_UPDATE_INTERVAL,
    TYPE_INCIDENTS,
    TYPE_DEPARTMENTS,
    KEY_ACTIVE_OPS,
    KEY_DEPLOYED_FF,
    KEY_COMPLETED
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    pages = entry.options.get(CONF_PAGES, [])
    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    
    if not pages:
        return

    session = aiohttp.ClientSession()
    coordinator = FireDeptCoordinator(hass, session, pages, update_interval)
    
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for idx, page in enumerate(pages):
        entities.append(FireDeptSensor(coordinator, entry, page, idx))

    async_add_entities(entities)


class FireDeptCoordinator(DataUpdateCoordinator):
    """Fetch data for all pages."""
    def __init__(self, hass, session, pages, interval_minutes):
        self.session = session
        self.pages = pages
        super().__init__(
            hass, 
            _LOGGER, 
            name=DOMAIN, 
            update_interval=timedelta(minutes=interval_minutes)
        )

    async def _async_update_data(self):
        data = {}
        for idx, page in enumerate(self.pages):
            url = page["url"]
            p_type = page["type"]
            data[idx] = await self.fetch_and_parse(url, p_type)
        return data

    async def fetch_and_parse(self, url, p_type):
        data_list = []
        try:
            async with async_timeout.timeout(15):
                async with self.session.get(url) as response:
                    text = await response.text(encoding='ISO-8859-1')
            
            soup = BeautifulSoup(text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    raw_data = [ele.text.strip() for ele in cols]
                    
                    # Skip Headers
                    if not raw_data or "Zeit" in str(raw_data) or "Feuerwehr" in str(raw_data):
                        continue
                        
                    formatted_row = self.process_row_smart(raw_data, p_type)
                    if formatted_row:
                        data_list.append(formatted_row)
                        
            return data_list
        except Exception as e:
            _LOGGER.error(f"Error parsing {url}: {e}")
            return []

    def process_row_smart(self, row, p_type):
        """Smartly detect columns based on Time format."""
        try:
            # 1. Find the index of the Time column (contains :)
            time_idx = -1
            for i, col in enumerate(row):
                if ":" in col or "std" in col.lower(): # Matches "12:00" or "< 1 std."
                    time_idx = i
                    break
            
            if time_idx == -1: return None # No time found, invalid row

            # 2. Extract relative to Time
            raw_time = row[time_idx]
            incident_type = row[time_idx - 1] if time_idx >= 1 else "-"
            
            district = "-"
            location = "-"

            if p_type == TYPE_INCIDENTS:
                # Layout: [Hidden] [District] [Location] [Type] [Time]
                # If Time is at index 4: Type=3, Loc=2, Dist=1
                location = row[time_idx - 2] if time_idx >= 2 else "-"
                district = self.clean_text(row[time_idx - 3]) if time_idx >= 3 else "-"

            elif p_type == TYPE_DEPARTMENTS:
                # Layout: [Hidden] [Department] [Type] [Time]
                # If Time is at index 3: Type=2, Dept=1
                district = self.clean_text(row[time_idx - 2]) if time_idx >= 2 else "-" # Dept Name in District slot
                location = "-"

            date_str, time_str = self.split_datetime(raw_time)

            return [date_str, time_str, district, location, incident_type]

        except Exception as e:
            return None

    def clean_text(self, text):
        """Remove leading numbers."""
        return re.sub(r'^\d+\s*', '', text)

    def split_datetime(self, raw_str):
        """Split Date and Time."""
        match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*(.*)', raw_str)
        if match:
            return match.group(1), match.group(2)
        return "-", raw_str


class FireDeptSensor(SensorEntity):
    """Dynamic Sensor."""
    _attr_has_entity_name = True 

    def __init__(self, coordinator, entry, page_config, page_index):
        self.coordinator = coordinator
        self._entry = entry
        self._page = page_config
        self._idx = page_index
        
        t_key = page_config.get("name")
        self._attr_translation_key = t_key 
        
        if t_key not in [KEY_ACTIVE_OPS, KEY_DEPLOYED_FF, KEY_COMPLETED]:
             if page_config.get("name"):
                 self._attr_name = page_config["name"]
                 self._attr_translation_key = None 

        self._attr_unique_id = f"{entry.entry_id}_{page_index}"
        self._attr_icon = "mdi:fire-truck" if page_config["type"] == TYPE_INCIDENTS else "mdi:shield-account"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="NÖ Landeswarnzentrale",
            model="WASTL Scraper",
        )

    @property
    def native_value(self):
        data = self.coordinator.data.get(self._idx, [])
        return len(data)

    @property
    def extra_state_attributes(self):
        return {
            "data_list": self.coordinator.data.get(self._idx, []),
            "url": self._page["url"]
        }
