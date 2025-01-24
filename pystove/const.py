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

from enum import IntEnum, IntFlag

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


class BurnPhase(IntEnum):
    IGNITION = 0
    BURN = 1
    GLOW = 4
    STANDBY = 5


class FileOpenFailedError(Exception):
    """File Open request unsuccessful."""


class FileWriteFailedError(Exception):
    """File Write request unsuccessful."""


class MaintenanceAlarm(IntFlag):
    """Maintenance alarms."""

    BACKUP_BATTERY_LOW = 1
    O2_SENSOR_FAULT = 2
    O2_SENSOR_OFFSET = 4
    STOVE_TEMP_SENSOR_FAULT = 8
    ROOM_TEMP_SENSOR_FAULT = 16
    COMM_FAULT = 32
    ROOM_TEMP_SENSOR_BATTERY_LOW = 64


class NightLoweringState(IntEnum):
    """Night lowering states."""

    DISABLED = 0
    INIT = 1
    DAY = 2
    NIGHT = 3
    MANUAL_NIGHT = 4


class OperationMode(IntEnum):
    """Stove operation modes."""

    INIT = 0
    SELF_TEST = 1
    NORMAL = 2
    TEMPERATURE_FAULT = 3
    O2_FAULT = 4
    CALIBRATION = 5
    SAFETY = 6
    MANUAL = 7
    MOTOR_TEST = 8
    SLOW_COMBUSTION = 9
    LOW_VOLTAGE = 10


class SafetyAlarm(IntFlag):
    """Stove Safety Alarms."""

    VALVE_1_FAULT = 1
    VALVE_2_FAULT = 2
    VALVE_3_FAULT = 4
    BAD_CONFIGURATION = 8
    VALVE_1_DISCONNECTED = 16
    VALVE_2_DISCONNECTED = 32
    VALVE_3_DISCONNECTED = 64
    VALVE_1_CALIBRATION_ERROR = 128
    VALVE_2_CALIBRATION_ERROR = 256
    VALVE_3_CALIBRATION_ERROR = 512
    CHIMNEY_OVERHEAT = 1024
    DOOR_OPEN_TOO_LONG = 2048
    MANUAL_SAFETY_ALARM = 4096
    STOVE_SENSOR_FAULT = 8192


class SelfTestState(IntEnum):
    """Self test states."""

    FAILED = 0
    PASSED = 1
    RUNNING = 2
    NOT_COMPLETED = 3
    NOT_STARTED = 4
