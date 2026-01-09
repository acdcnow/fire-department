"""Constants for the Fire Department integration."""
from datetime import timedelta

DOMAIN = "fire_department"
CONF_PAGES = "pages"
CONF_REGION = "region"
CONF_UPDATE_INTERVAL = "update_interval"

# Parser Types
TYPE_INCIDENTS = "incidents"       # For Current/Historic (4+ cols)
TYPE_DEPARTMENTS = "departments"   # For Active FF (3 cols)

DEFAULT_NAME = "Fire Department Info"
DEFAULT_UPDATE_INTERVAL = 60 # Minutes

# Sensor Keys (Used for translation lookups)
KEY_ACTIVE_OPS = "active_operations"
KEY_DEPLOYED_FF = "deployed_fire_brigade"
KEY_COMPLETED = "completed_missions"

PARSER_TYPES = {
    TYPE_INCIDENTS: "Incidents List (Current/History)",
    TYPE_DEPARTMENTS: "Active Departments List",
}

# Catalog of Regions
CATALOG = {
    "lower_austria": [
        {
            "name": KEY_ACTIVE_OPS,
            "url": "https://www.feuerwehr-krems.at/codepages/wastl/wastlmain/Land_EinsatzAktuell.asp",
            "type": TYPE_INCIDENTS
        },
        {
            "name": KEY_DEPLOYED_FF,
            "url": "https://www.feuerwehr-krems.at/codepages/wastl/wastlmain/Land_FFimEinsatz.asp",
            "type": TYPE_DEPARTMENTS
        },
        {
            "name": KEY_COMPLETED,
            "url": "https://www.feuerwehr-krems.at/CodePages/Wastl/WastlMain/Land_EinsatzHistorie.asp",
            "type": TYPE_INCIDENTS
        }
    ],
    "vienna": [],
    "upper_austria": [],
    "styria": [],
    "salzburg": [],
    "burgenland": [],
    "carinthia": [],
    "tyrol": [],
    "vorarlberg": []
}