# Fire Department Info (Austria)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-2.1.0-blue.svg)]()
[![Maintainer](https://img.shields.io/badge/maintainer-acdcnow-orange.svg)]()

A Home Assistant integration that retrieves fire department operations and incident data for Austria. It primarily scrapes the "WASTL" (Warn- und Alarmsystem) information to provide real-time updates on active incidents, deployed fire brigades, and completed missions.

## Features

* **Real-time Incident Monitoring**: View active fire department operations.
* **Detailed Attributes**: Access lists of specific incidents, locations, and timestamps via attributes.
* **Configurable**: Set your preferred update interval and region via the UI.
* **Sensor Types**:
    * **Active Operations**: Count of currently ongoing incidents.
    * **Deployed Fire Brigades**: Count of fire brigades currently deployed.
    * **Completed Missions**: Count of missions completed (history).

## Supported Regions

Currently, the following regions are selectable, but **data sources are fully configured for**:

* **Lower Austria (Niederösterreich)** ✅

*Other regions (Vienna, Upper Austria, Styria, etc.) are present in the configuration for future expansion but do not yet have active data URLs defined.*

## Installation

### Option 1: HACS (Recommended)

1.  Open HACS in your Home Assistant instance.
2.  Go to **Integrations** > click the **3 dots** (top right) > **Custom repositories**.
3.  Add the URL of this repository.
4.  Category: **Integration**.
5.  Click **Add** and then **Download**.
6.  Restart Home Assistant.

### Option 2: Manual

1.  Download the `custom_components/fire_department` folder from this repository.
2.  Copy the folder into your Home Assistant's `config/custom_components/` directory.
3.  Restart Home Assistant.

## Configuration

1.  Go to **Settings** > **Devices & Services**.
2.  Click **+ Add Integration**.
3.  Search for **Fire Department Info**.
4.  Follow the setup wizard:
    * **Name**: Give your integration a custom name (default: Fire Department Info).
    * **Region**: Select your Austrian federal state (e.g., Lower Austria).
    * **Update Interval**: Set how often data should be fetched (minutes).

### Options

You can change settings later by clicking **Configure** on the integration entry:
* Change the update interval.
* Add or remove specific pages/sensors manually if needed.

## Sensors

The integration creates the following sensors (entity IDs depend on your configuration name):

| Sensor Name | ID Example | Description |
| :--- | :--- | :--- |
| **Active Operations** | `sensor.fire_department_info_active_operations` | Number of current incidents. |
| **Deployed Fire Brigades** | `sensor.fire_department_info_deployed_fire_brigades` | Number of brigades currently in action. |
| **Completed Missions** | `sensor.fire_department_info_completed_missions` | Number of missions finished recently. |

## Dashboards

* Preconfigured dashboard files for each sensor and the overview map as iframe in folder "dashboard files" copy the yaml code into a blank dashboard.
* adjust the sensor name based on your needs and results in your devide and entity list.

### Attributes
Each sensor contains a `data_list` attribute with the raw parsed rows, useful for displaying in Markdown cards or Flex Table cards.

**Example `data_list` structure:**
```json
[
  ["DD.MM.YYYY", "HH:mm", "City", "street 123", "T1 - Vehicle Recovery"],
  ...
]
