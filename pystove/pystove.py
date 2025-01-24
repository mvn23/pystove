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

import asyncio
from datetime import datetime, time, timedelta
from enum import IntEnum
import json
import logging
import struct

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
import defusedxml.ElementTree as ET

from . import const as c

_LOGGER = logging.getLogger(__name__)

FILE_MODE = "mode"
FILE_NAME = "file_name"
FILE_SIZE = "file_size"

FILENAME_INFO = "info.xml"

IDENT_IP = "ip"
IDENT_MDNS = "mdns"
IDENT_NAME = "name"
IDENT_SSID = "ssid"

INFO_NODE_NAME = "Name"
INFO_NODE_TYPE = "StoveType"

KEY_ENABLE = "enable"
KEY_LEVEL = "level"
KEY_RESPONSE = "response"

HTTP_HEADERS = {"Accept": "application/json"}

RESPONSE_OK = "OK"
RESPONSE_SUCCESS = "success"

STOVE_ACCESSPOINT_URL = "/esp/get_current_accesspoint"
STOVE_BURN_LEVEL_URL = "/set_burn_level"
STOVE_CLOSE_FILE_URL = "/close_file"
STOVE_DATA_URL = "/get_stove_data"
STOVE_DELETE_FILE_URL = "/delete_file"
STOVE_ID_URL = "/esp/get_identification"
STOVE_LIVE_DATA_URL = "/get_live_data"
STOVE_NIGHT_LOWERING_OFF_URL = "/set_night_lowering_off"
STOVE_NIGHT_LOWERING_ON_URL = "/set_night_lowering_on"
STOVE_NIGHT_TIME_URL = "/set_night_time"
STOVE_OPEN_FILE_URL = "/open_file"
STOVE_READ_OPEN_FILE_URL = "/read_open_file"
STOVE_REMOTE_REFILL_ALARM_URL = "/set_remote_refill_alarm"
STOVE_SET_TIME_URL = "/set_time"
STOVE_SELFTEST_RESULT_URL = "/get_selftest_result"
STOVE_SELFTEST_START_URL = "/start_selftest"
STOVE_START_URL = "/start"
STOVE_WRITE_OPEN_FILE_URL = "/write_open_file"

YEAR = "year"
MONTH = "month"
DAY = "day"
HOURS = "hours"
MINUTES = "minutes"
SECONDS = "seconds"


class OpenFileMode(IntEnum):
    """Modes used to open files on the stove."""

    WRITE = 0
    READ = 1


class Stove:
    """Abstraction of a Stove object."""

    @classmethod
    async def create(cls, stove_host, skip_ident=False):
        """Async create the Stove object."""
        self = cls()
        self.stove_host = stove_host
        self.algo_version = None
        self.name = None
        self.series = None
        self.stove_ip = None
        self.stove_mdns = None
        self.stove_ssid = None
        self._session = aiohttp.ClientSession(headers=HTTP_HEADERS)
        if not skip_ident:
            await self._identify()
        return self

    async def destroy(self):
        await self._session.close()

    async def get_data(self):
        """Call get_raw_data, process result before returning."""
        data = await self.get_raw_data()
        if data is None:
            return
        phase = c.PHASE[data[c.DATA_PHASE]]
        stove_datetime = datetime(
            data[YEAR],
            data[MONTH],
            data[DAY],
            data[HOURS],
            data[MINUTES],
            data[SECONDS],
        )
        time_to_refuel = timedelta(
            hours=data[c.DATA_NEW_FIREWOOD_HOURS],
            minutes=data[c.DATA_NEW_FIREWOOD_MINUTES],
        )
        refuel_estimate = stove_datetime + time_to_refuel
        safety_alarms = self._get_safety_alarms_text(data[c.DATA_SAFETY_ALARMS])
        operation_mode = c.OPERATION_MODES[data[c.DATA_OPERATION_MODE]]
        night_lowering = c.NIGHT_LOWERING_STATES[data[c.DATA_NIGHT_LOWERING]]
        # Stove uses 24:00 for end of day
        nighttime_start = time(
            hour=data[c.DATA_NIGHT_BEGIN_HOUR] % 24,
            minute=data[c.DATA_NIGHT_BEGIN_MINUTE],
        )
        nighttime_end = time(
            hour=data[c.DATA_NIGHT_END_HOUR] % 24, minute=data[c.DATA_NIGHT_END_MINUTE]
        )
        stove_version = (
            f"{data[c.DATA_FIRMWARE_VERSION_MAJOR]}"
            f".{data[c.DATA_FIRMWARE_VERSION_MINOR]}"
            f".{data[c.DATA_FIRMWARE_VERSION_BUILD]}"
        )
        remote_version = (
            f"{data[c.DATA_REMOTE_VERSION_MAJOR]}"
            f".{data[c.DATA_REMOTE_VERSION_MINOR]}"
            f".{data[c.DATA_REMOTE_VERSION_BUILD]}"
        )
        for item in (
            c.DATA_STOVE_TEMPERATURE,
            c.DATA_ROOM_TEMPERATURE,
            c.DATA_OXYGEN_LEVEL,
        ):
            data[item] = float(data[item] / 100)
        processed_data = {
            c.DATA_ALGORITHM: data[c.DATA_ALGORITHM],
            c.DATA_BURN_LEVEL: data[c.DATA_BURN_LEVEL],
            c.DATA_MAINTENANCE_ALARMS: c.MaintenanceAlarm(
                data[c.DATA_MAINTENANCE_ALARMS]
            ),
            c.DATA_MESSAGE_ID: data[c.DATA_MESSAGE_ID],
            c.DATA_NEW_FIREWOOD_ESTIMATE: refuel_estimate,
            c.DATA_NIGHT_BEGIN_TIME: nighttime_start,
            c.DATA_NIGHT_END_TIME: nighttime_end,
            c.DATA_NIGHT_LOWERING: night_lowering,
            c.DATA_OPERATION_MODE: operation_mode,
            c.DATA_OXYGEN_LEVEL: data[c.DATA_OXYGEN_LEVEL],
            c.DATA_PHASE: phase,
            c.DATA_REFILL_ALARM: data[c.DATA_REFILL_ALARM],
            c.DATA_REMOTE_REFILL_ALARM: data[c.DATA_REMOTE_REFILL_ALARM],
            c.DATA_REMOTE_VERSION: remote_version,
            c.DATA_ROOM_TEMPERATURE: data[c.DATA_ROOM_TEMPERATURE],
            c.DATA_SAFETY_ALARMS: safety_alarms,
            c.DATA_STOVE_TEMPERATURE: data[c.DATA_STOVE_TEMPERATURE],
            c.DATA_TIME_SINCE_REMOTE_MSG: data[c.DATA_TIME_SINCE_REMOTE_MSG],
            c.DATA_DATE_TIME: stove_datetime,
            c.DATA_TIME_TO_NEW_FIREWOOD: time_to_refuel,
            c.DATA_UPDATING: data[c.DATA_UPDATING],
            c.DATA_VALVE1_POSITION: data[c.DATA_VALVE1_POSITION],
            c.DATA_VALVE2_POSITION: data[c.DATA_VALVE2_POSITION],
            c.DATA_VALVE3_POSITION: data[c.DATA_VALVE3_POSITION],
            c.DATA_FIRMWARE_VERSION: stove_version,
        }
        return processed_data

    async def get_live_data(self):
        """Get 'live' temp and o2 data from the last 2 hours."""
        bin_arr = bytearray(
            await self._get("http://" + self.stove_host + STOVE_LIVE_DATA_URL), "utf-8"
        )
        response_length = len(bin_arr)
        if response_length % 8 != 0:
            _LOGGER.error("get_live_data got unexpected response from stove.")
            return
        data_out = {
            c.DATA_STOVE_TEMPERATURE: [],
            c.DATA_OXYGEN_LEVEL: [],
        }
        number_of_datapoints = int(response_length / 8)
        for i in range(number_of_datapoints):
            data_out[c.DATA_STOVE_TEMPERATURE].append(
                (
                    bin_arr[i * 4] << 4
                    | bin_arr[i * 4 + 1] << 0
                    | bin_arr[i * 4 + 2] << 12
                    | bin_arr[i * 4 + 3] << 8
                )
                / 100
            )
            data_out[c.DATA_OXYGEN_LEVEL].append(
                (
                    bin_arr[(number_of_datapoints + i) * 4 + 0] << 4
                    | bin_arr[(number_of_datapoints + i) * 4 + 1] << 0
                    | bin_arr[(number_of_datapoints + i) * 4 + 2] << 12
                    | bin_arr[(number_of_datapoints + i) * 4 + 3] << 8
                )
                / 100
            )
        return data_out

    async def get_raw_data(self):
        """Request an update from the stove, return raw result."""
        return await self._get_json("http://" + self.stove_host + STOVE_DATA_URL)

    def self_test(self, delay=3, processed=True):
        """Return self test async generator."""
        return _SelfTest(self, delay, processed)

    async def set_burn_level(self, burn_level):
        """Set the desired burnlevel."""
        data = {KEY_LEVEL: burn_level}
        json_str = await self._post(
            "http://" + self.stove_host + STOVE_BURN_LEVEL_URL, data
        )
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(KEY_RESPONSE) == RESPONSE_OK

    async def set_night_lowering(self, state=None):
        """Switch/toggle night lowering (True=on, False=off, None=toggle)."""
        if state is None:
            data = await self.get_raw_data()
            # 0 == Off
            # 2 == On outside night hours
            # 3 == On inside night hours
            # When does night_lowering == 1 happen?
            cur_state = data[c.DATA_NIGHT_LOWERING] > 0
        else:
            cur_state = not state
        url = STOVE_NIGHT_LOWERING_OFF_URL if cur_state else STOVE_NIGHT_LOWERING_ON_URL
        result = await self._get_json("http://" + self.stove_host + url)
        return result.get(KEY_RESPONSE) == RESPONSE_OK

    async def set_night_lowering_hours(self, start=None, end=None):
        """Set night lowering start and end time."""
        if start is None or end is None:
            data = await self.get_data()
        start = start or data[c.DATA_NIGHT_BEGIN_TIME]
        end = end or data[c.DATA_NIGHT_END_TIME]
        data = {
            c.DATA_BEGIN_HOUR: start.hour,
            c.DATA_BEGIN_MINUTE: start.minute,
            c.DATA_END_HOUR: end.hour,
            c.DATA_END_MINUTE: end.minute,
        }
        json_str = await self._post(
            "http://" + self.stove_host + STOVE_NIGHT_TIME_URL, data
        )
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(KEY_RESPONSE) == RESPONSE_OK

    async def set_remote_refill_alarm(self, state=None):
        """Set or toggle remote_refill_alarm setting."""
        if state is None:
            data = await self.get_raw_data()
            cur_state = data[c.DATA_REMOTE_REFILL_ALARM] == 1
        else:
            cur_state = not state
        data = {KEY_ENABLE: 0 if cur_state else 1}
        json_str = await self._post(
            "http://" + self.stove_host + STOVE_REMOTE_REFILL_ALARM_URL, data
        )
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(KEY_RESPONSE) == RESPONSE_OK

    async def set_time(self, new_time=None):
        """Set the time and date of the stove."""
        if new_time is None:
            new_time = datetime.now()
        data = {
            YEAR: new_time.year,
            MONTH: new_time.month - 1,  # Stove month input is 0 based.
            DAY: new_time.day,
            HOURS: new_time.hour,
            MINUTES: new_time.minute,
            SECONDS: new_time.second,
        }
        json_str = await self._post(
            "http://" + self.stove_host + STOVE_SET_TIME_URL, data
        )
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(KEY_RESPONSE) == RESPONSE_OK

    async def start(self):
        """Start the ignition phase."""
        result = await self._get_json("http://" + self.stove_host + STOVE_START_URL)
        return result.get(KEY_RESPONSE) == RESPONSE_OK

    async def write_text_file(self, filename, text):
        async with _StoveWritableFile(self, filename) as f:
            await f.write_text(text)

    async def write_binary_file(self, filename, data):
        async with _StoveWritableFile(self, filename) as f:
            await f.write_binary(data)

    async def delete_file(self, filename):
        json_str = await self._post(
            "http://" + self.stove_host + STOVE_NIGHT_TIME_URL,
            {c.DATA_FILENAME: filename},
        )
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return False
        return json.loads(json_str).get(KEY_RESPONSE) == RESPONSE_OK

    async def _identify(self):
        """Get identification and set the properties on the object."""

        async def get_identification():
            """Get stove name, IP and MDNS"""
            stove_id = await self._get_json("http://" + self.stove_host + STOVE_ID_URL)
            if not stove_id:
                _LOGGER.error("Unable to read stove identity informations.")
                return

            if IDENT_NAME in stove_id:
                self.name = stove_id[IDENT_NAME]
            else:
                _LOGGER.warning("Unable to read stove name.")

            if IDENT_IP in stove_id:
                self.stove_ip = stove_id[IDENT_IP]
            else:
                _LOGGER.warning("Unable to read stove IP.")

            if IDENT_MDNS in stove_id:
                self.stove_mdns = stove_id[IDENT_MDNS]
                self.mac_address = int(self.stove_mdns[-12:], 16) & 0xFDFFFFFFFFFF

            else:
                _LOGGER.warning("Unable to read stove MDNS.")

        async def get_ssid():
            """Get stove SSID."""
            result = await self._get_json(
                "http://" + self.stove_host + STOVE_ACCESSPOINT_URL
            )
            stove_ssid = result.get(IDENT_SSID)
            if stove_ssid is None:
                _LOGGER.warning("Unable to read stove SSID.")
                return
            self.stove_ssid = stove_ssid

        async def get_version_info():
            """Get stove version info."""
            async with _StoveFile(self, FILENAME_INFO) as f:
                xml_str = await f.read()
                try:
                    xml_root = ET.fromstring(xml_str)
                    self.algo_version = xml_root.find(INFO_NODE_NAME).text
                    self.series = xml_root.find(INFO_NODE_TYPE).text
                except ET.ParseError:
                    _LOGGER.warning("Invalid XML. Could not get version info.")
                except AttributeError:
                    _LOGGER.warning("Missing key in version info XML.")

        await asyncio.gather(
            *[
                get_identification(),
                get_ssid(),
                get_version_info(),
            ]
        )

    async def _self_test_result(self):
        """Get self test result."""
        count = 0
        result = None
        while True:
            # Error prone, retry up to 3 times
            result = await self._get_json(
                "http://" + self.stove_host + STOVE_SELFTEST_RESULT_URL
            )
            if result == {}:
                continue
            if not result.get("reponse"):  # NOT A TYPO!!!
                break
            if count >= 3:
                return
            count = count + 1
            await asyncio.sleep(3)
        return result

    async def _self_test_start(self):
        """Request self test start."""
        result = await self._get_json(
            "http://" + self.stove_host + STOVE_SELFTEST_START_URL
        )
        return result.get(KEY_RESPONSE) == RESPONSE_OK

    def _get_safety_alarms_text(self, bitmask):
        """Process safety alarms bitmask, return a list of strings."""
        num_alarms = len(c.SAFETY_ALARMS)
        ret = []
        for i in range(num_alarms):
            if 1 << i & bitmask:
                ret.append(c.SAFETY_ALARMS[i])
        return ret

    async def _get_json(self, url):
        """Get data from url, interpret as json, return result."""
        json_str = await self._get(url)
        if json_str is None:
            _LOGGER.error("Got empty or no response from stove.")
            return {}
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as exc:
            _LOGGER.error("Could not decode received data as json: %s", exc.doc)
            _LOGGER.error("Error was: %s", exc.msg)
            return {}
        return result

    async def _get(self, url):
        """Get data from url, return response."""
        try:
            async with self._session.get(url) as response:
                return await response.text()
        except ClientConnectorError:
            _LOGGER.error("Could not connect to stove.")

    async def _post(self, url, data):
        """Post data to url, return response."""
        try:
            async with self._session.post(
                url, data=json.dumps(data, separators=(",", ":"))
            ) as response:
                return await response.text()
        except ClientConnectorError:
            _LOGGER.error("Could not connect to stove.")


class _SelfTest:
    """Self test async generator."""

    def __init__(self, stove, delay, processed=True):
        self.stove = stove
        self.delay = delay
        self.processed = processed
        self.test_started = False
        self.test_finished = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        async def get_result():
            """Get intermediate test results."""

            def process_dict(in_dict):
                """Process dict values."""
                if not self.processed:
                    return in_dict
                out_dict = {}
                for k, v in in_dict.items():
                    out_dict[k] = c.SELF_TEST_VALUES[v]
                return out_dict

            intermediate_raw = await self.stove._self_test_result()
            if intermediate_raw is None:
                return None
            else:
                intermediate = process_dict(intermediate_raw)
                if 2 not in intermediate_raw.values():
                    self.test_finished = True
                return intermediate

        if not self.test_started:
            if await self.stove._self_test_start():
                self.test_started = True
                return await get_result()
            else:
                raise StopAsyncIteration
        if self.test_finished:
            raise StopAsyncIteration

        await asyncio.sleep(self.delay)
        return await get_result()


class _StoveFile:
    """Context manager for read-only files on the stove."""

    def __init__(self, stove, path):
        """Initialize the context manager."""
        self.stove = stove
        self.base_url = "http://" + stove.stove_host
        self.data = {FILE_NAME: path, FILE_MODE: OpenFileMode.READ}
        self.file_size = None

    async def __aenter__(self):
        """Open a file within a context."""
        try:
            json_str = await self.stove._post(
                self.base_url + STOVE_OPEN_FILE_URL, self.data
            )
            if json_str is None:
                raise ClientConnectorError
            response_data = json.loads(json_str)
            if response_data.get(RESPONSE_SUCCESS) != 1:
                raise c.FileOpenFailedError
            self.file_size = response_data.get(FILE_SIZE)
            return self
        except (ClientConnectorError, c.FileOpenFailedError):
            await self.stove._get(self.base_url + STOVE_CLOSE_FILE_URL)
            raise

    async def __aexit__(self, *args):
        """Close the file."""
        await self.stove._get(self.base_url + STOVE_CLOSE_FILE_URL)

    async def read(self):
        """Read the file."""
        return await self.stove._post(self.base_url + STOVE_READ_OPEN_FILE_URL, {})


class _StoveWritableFile(_StoveFile):
    """Context manager for writable files on the stove."""

    def __init__(self, stove, path):
        """Initialize the context manager."""
        super().__init__(stove, path)
        self.data = {FILE_NAME: path, FILE_MODE: OpenFileMode.WRITE}

    async def write_text(self, text, offset=0):
        """Write text to the file."""
        await self.write_binary(text.encode("utf-8", offset))

    async def write_binary(self, data, offset=0):
        """Write data to the file."""
        # write_open_file expects binary data:
        # uint16 Size of binary data;
        # uint32 Offset to write to;
        # uint8[1024] data
        data_length = len(data)
        if data_length > 1024:
            raise RuntimeError("Data too long (>1024 bytes)")
        size = 2 + 4 + data_length
        byte_array = struct.pack(f"<HI{data_length}s", size, offset, data)

        try:
            reader, writer = await asyncio.open_connection(self.stove.stove_host, 80)
            request_string = (
                f"POST {STOVE_WRITE_OPEN_FILE_URL} HTTP/1.1 \r\n"
                f"content-length: {data_length} \r\n"
                "Content-Type: binary \r\n"
                "\r\n"
            )
            writer.write(request_string.encode("utf-8"))
            writer.write(byte_array)
            await writer.drain()
            response = await reader.read(2)
            if response != b"OK":
                raise c.FileWriteFailedError
        finally:
            writer.close()
