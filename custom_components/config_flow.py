"""Config flow for Fire Department integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN, 
    CONF_PAGES,
    CONF_UPDATE_INTERVAL,
    CATALOG, 
    TYPE_INCIDENTS, 
    TYPE_DEPARTMENTS, 
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

class FireDeptConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            region = user_input.get("region", "lower_austria")
            name = user_input.get("name", DEFAULT_NAME)
            interval = user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            
            default_pages = CATALOG.get(region, [])
            
            return self.async_create_entry(
                title=name, 
                data={},
                options={
                    CONF_PAGES: default_pages,
                    CONF_UPDATE_INTERVAL: interval
                }
            )

        region_options = sorted(list(CATALOG.keys()))
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default=DEFAULT_NAME): str,
                vol.Required("region", default="lower_austria"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=region_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="region" 
                    )
                ),
                vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=600)
                ),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FireDeptOptionsFlowHandler(config_entry)


class FireDeptOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        # SAFETY FIX: Ensure options is a dict even if currently None
        self.options = dict(config_entry.options) if config_entry.options else {}
        self.pages = self.options.get(CONF_PAGES, [])

    async def async_step_init(self, user_input=None):
        """Manage global options."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["global_settings", "add_page", "remove_page"]
        )

    async def async_step_global_settings(self, user_input=None):
        """Step to change update interval."""
        if user_input is not None:
            self.options[CONF_UPDATE_INTERVAL] = user_input["update_interval"]
            return self.async_create_entry(title="", data=self.options)

        current_interval = self.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        
        return self.async_show_form(
            step_id="global_settings",
            data_schema=vol.Schema({
                vol.Required("update_interval", default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=600)
                ),
            })
        )

    async def async_step_add_page(self, user_input=None):
        if user_input is not None:
            new_page = {
                "name": user_input["name"],
                "url": user_input["url"],
                "type": user_input["type"]
            }
            self.pages.append(new_page)
            self.options[CONF_PAGES] = self.pages
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="add_page",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("url"): str,
                vol.Required("type", default=TYPE_INCIDENTS): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[TYPE_INCIDENTS, TYPE_DEPARTMENTS],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="parser_type"
                    )
                ),
            })
        )

    async def async_step_remove_page(self, user_input=None):
        if user_input is not None:
            removed_indexes = [int(i) for i in user_input["pages_to_remove"]]
            self.pages = [page for idx, page in enumerate(self.pages) if idx not in removed_indexes]
            self.options[CONF_PAGES] = self.pages
            return self.async_create_entry(title="", data=self.options)

        if not self.pages:
            return self.async_abort(reason="no_pages")

        options = [
            selector.SelectOptionDict(value=str(idx), label=f"{p.get('name', 'Page ' + str(idx))}")
            for idx, p in enumerate(self.pages)
        ]

        return self.async_show_form(
            step_id="remove_page",
            data_schema=vol.Schema({
                vol.Required("pages_to_remove"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                )
            })
        )