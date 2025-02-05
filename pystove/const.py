# This file is part of pystove.
#
# pystove is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pystove is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pystove.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 Milan van Nugteren
#

DATA_ALGORITHM = "algorithm"
DATA_BEGIN_HOUR = "begin_hour"
DATA_BEGIN_MINUTE = "begin_minute"
DATA_END_HOUR = "end_hour"
DATA_END_MINUTE = "end_minute"
DATA_BURN_LEVEL = "burn_level"
DATA_DATE_TIME = "date_time"
DATA_FIRMWARE_VERSION = "firmware_version"
DATA_FIRMWARE_VERSION_BUILD = "version_build"
DATA_FIRMWARE_VERSION_MAJOR = "version_major"
DATA_FIRMWARE_VERSION_MINOR = "version_minor"
DATA_MAINTENANCE_ALARMS = "maintenance_alarms"
DATA_MESSAGE_ID = "message_id"
DATA_NEW_FIREWOOD_ESTIMATE = "new_fire_wood_estimate"
DATA_NEW_FIREWOOD_HOURS = "new_fire_wood_hours"
DATA_NEW_FIREWOOD_MINUTES = "new_fire_wood_minutes"
DATA_NIGHT_BEGIN_HOUR = "night_begin_hour"
DATA_NIGHT_BEGIN_MINUTE = "night_begin_minute"
DATA_NIGHT_BEGIN_TIME = "night_begin_time"
DATA_NIGHT_END_HOUR = "night_end_hour"
DATA_NIGHT_END_MINUTE = "night_end_minute"
DATA_NIGHT_END_TIME = "night_end_time"
DATA_NIGHT_LOWERING = "night_lowering"
DATA_OPERATION_MODE = "operation_mode"
DATA_OXYGEN_LEVEL = "oxygen_level"
DATA_PHASE = "phase"
DATA_REFILL_ALARM = "refill_alarm"
DATA_REMOTE_REFILL_ALARM = "remote_refill_alarm"
DATA_REMOTE_VERSION = "remote_version"
DATA_REMOTE_VERSION_BUILD = "remote_version_build"
DATA_REMOTE_VERSION_MAJOR = "remote_version_major"
DATA_REMOTE_VERSION_MINOR = "remote_version_minor"
DATA_ROOM_TEMPERATURE = "room_temperature"
DATA_SAFETY_ALARMS = "safety_alarms"
DATA_STOVE_TEMPERATURE = "stove_temperature"
DATA_TEST_CONFIGURATION = "configuration"
DATA_TEST_O2_SENSOR = "o2_sensor"
DATA_TEST_TEMP_SENSOR = "t10_sensor"
DATA_TEST_VALVE1 = "valve_primary"
DATA_TEST_VALVE2 = "valve_secondary"
DATA_TEST_VALVE3 = "valve_tertiary"
DATA_TIME_SINCE_REMOTE_MSG = "time_since_remote_msg"
DATA_TIME_TO_NEW_FIREWOOD = "time_to_new_fire_wood"
DATA_UPDATING = "updating"
DATA_VALVE1_POSITION = "valve1_position"
DATA_VALVE2_POSITION = "valve2_position"
DATA_VALVE3_POSITION = "valve3_position"

MAINTENANCE_ALARMS = [
    "Stove Backup Battery Low",
    "O2 Sensor Fault",
    "O2 Sensor Offset",
    "Stove Temperature Sensor Fault",
    "Room Temperature Sensor Fault",
    "Communication Fault",
    "Room Temperature Sensor Battery Low",
]

NIGHT_LOWERING_STATES = [
    "Disabled",
    "Init",
    "Day",
    "Night",
    "Manual Night",
]

OPERATION_MODES = [
    "Init",
    "Self Test",
    "Normal",
    "Temperature Fault",
    "O2 Fault",
    "Calibration",
    "Safety",
    "Manual",
    "MotorTest",
    "Slow Combustion",
    "Low Voltage",
]

PHASE = [
    "Ignition",
    "Burn",
    "Burn",
    "Burn",
    "Glow",
    "Standby",
]

SAFETY_ALARMS = [
    "Valve Fault",
    "Valve Fault",
    "Valve Fault",
    "Bad Configuration",
    "Valve Disconnected",
    "Valve Disconnected",
    "Valve Disconnected",
    "Valve Calibration Error",
    "Valve Calibration Error",
    "Valve Calibration Error",
    "Chimney Overheat",
    "Door Open Too Long",
    "Manual Safety Alarm",
    "Stove Sensor Fault",
]

SELF_TEST_VALUES = [
    "Failed",
    "Passed",
    "Running",
    "Not Completed",
    "Not Started",
]


class FileOpenFailedError(Exception):
    """File Open request unsuccessful."""


class FileWriteFailedError(Exception):
    """File Write request unsuccessful."""
