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
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, time, timedelta

import aiohttp

from version import __version__


_LOGGER = logging.getLogger(__name__)

DATA_ALGORITHM = 'algorithm'
DATA_BEGIN_HOUR = 'begin_hour'
DATA_BEGIN_MINUTE = 'begin_minute'
DATA_ENABLE = 'enable'
DATA_END_HOUR = 'end_hour'
DATA_END_MINUTE = 'end_minute'
DATA_BURN_LEVEL = 'burn_level'
DATA_DATE_TIME = 'date_time'
DATA_FILENAME = 'file_name'
DATA_IP = 'ip'
DATA_LEVEL = 'level'
DATA_MAINTENANCE_ALARMS = 'maintenance_alarms'
DATA_MESSAGE_ID = 'message_id'
DATA_MODE = 'mode'
DATA_NAME = 'name'
DATA_NEW_FIREWOOD_ESTIMATE = 'new_fire_wood_estimate'
DATA_NEW_FIREWOOD_HOURS = 'new_fire_wood_hours'
DATA_NEW_FIREWOOD_MINUTES = 'new_fire_wood_minutes'
DATA_NIGHT_BEGIN_HOUR = 'night_begin_hour'
DATA_NIGHT_BEGIN_MINUTE = 'night_begin_minute'
DATA_NIGHT_BEGIN_TIME = 'night_begin_time'
DATA_NIGHT_END_HOUR = 'night_end_hour'
DATA_NIGHT_END_MINUTE = 'night_end_minute'
DATA_NIGHT_END_TIME = 'night_end_time'
DATA_NIGHT_LOWERING = 'night_lowering'
DATA_OPERATION_MODE = 'operation_mode'
DATA_OXYGEN_LEVEL = 'oxygen_level'
DATA_PHASE = 'phase'
DATA_REFILL_ALARM = 'refill_alarm'
DATA_REMOTE_REFILL_ALARM = 'remote_refill_alarm'
DATA_REMOTE_VERSION = 'remote_version'
DATA_REMOTE_VERSION_BUILD = 'remote_version_build'
DATA_REMOTE_VERSION_MAJOR = 'remote_version_major'
DATA_REMOTE_VERSION_MINOR = 'remote_version_minor'
DATA_RESPONSE = 'response'
DATA_ROOM_TEMPERATURE = 'room_temperature'
DATA_SAFETY_ALARMS = 'safety_alarms'
DATA_SSID = 'ssid'
DATA_STOVE_TEMPERATURE = 'stove_temperature'
DATA_SUCCESS = 'success'
DATA_TEST_CONFIGURATION = 'configuration'
DATA_TEST_O2_SENSOR = 'o2_sensor'
DATA_TEST_TEMP_SENSOR = 't10_sensor'
DATA_TEST_VALVE1 = 'valve_primary'
DATA_TEST_VALVE2 = 'valve_secondary'
DATA_TEST_VALVE3 = 'valve_tertiary'
DATA_TIME_SINCE_REMOTE_MSG = 'time_since_remote_msg'
DATA_TIME_TO_NEW_FIRE_WOOD = 'time_to_new_fire_wood'
DATA_UPDATING = 'updating'
DATA_VALVE1_POSITION = 'valve1_position'
DATA_VALVE2_POSITION = 'valve2_position'
DATA_VALVE3_POSITION = 'valve3_position'
DATA_VERSION = 'version'
DATA_VERSION_BUILD = 'version_build'
DATA_VERSION_MAJOR = 'version_major'
DATA_VERSION_MINOR = 'version_minor'

DATA_YEAR = 'year'
DATA_MONTH = 'month'
DATA_DAY = 'day'
DATA_HOURS = 'hours'
DATA_MINUTES = 'minutes'
DATA_SECONDS = 'seconds'

HTTP_HEADERS = {
    "Accept": "application/json"
}

PHASE = [
    'Ignition',
    'Burn',
    'Burn',
    'Burn',
    'Glow',
    'Start'
]

RESPONSE_OK = 'OK'

STOVE_ACCESSPOINT_URL = '/esp/get_current_accesspoint'
STOVE_BURN_LEVEL_URL = '/set_burn_level'
STOVE_DATA_URL = '/get_stove_data'
STOVE_ID_URL = '/esp/get_identification'
STOVE_NIGHT_LOWERING_OFF_URL = '/set_night_lowering_off'
STOVE_NIGHT_LOWERING_ON_URL = '/set_night_lowering_on'
STOVE_NIGHT_TIME_URL = '/set_night_time'
STOVE_OPEN_FILE_URL = '/open_file'
STOVE_READ_OPEN_FILE_URL = '/read_open_file'
STOVE_REMOTE_REFILL_ALARM_URL = '/set_remote_refill_alarm'
STOVE_SET_TIME_URL = '/set_time'
STOVE_SELFTEST_RESULT_URL = '/get_selftest_result'
STOVE_SELFTEST_START_URL = '/start_selftest'
STOVE_START_URL = '/start'

UNKNOWN = 'Unknown'


class pystove():
    """Abstraction of a pystove object."""

    @classmethod
    async def create(cls, stove_host, loop=asyncio.get_event_loop(),
                     skip_ident=False):
        """Async create the pystove object."""
        self = cls()
        self.loop = loop
        self.stove_host = stove_host
        self.full_version = UNKNOWN
        self.name = UNKNOWN
        self.series = UNKNOWN
        self.stove_ip = UNKNOWN
        self.stove_ssid = UNKNOWN
        self.version = UNKNOWN
        self._session = aiohttp.ClientSession(headers=HTTP_HEADERS)
        if not skip_ident:
            await self._identify()
        return self

    async def destroy(self):
        await self._session.close()

    async def get_data(self):
        """Call get_raw_data, process result before returning."""
        data = await self.get_raw_data()
        phase = PHASE[data[DATA_PHASE]]
        stove_datetime = datetime(data[DATA_YEAR], data[DATA_MONTH],
                                  data[DATA_DAY], data[DATA_HOURS] ,
                                  data[DATA_MINUTES], data[DATA_SECONDS])
        time_to_refuel = timedelta(hours=data[DATA_NEW_FIREWOOD_HOURS],
                                   minutes=data[DATA_NEW_FIREWOOD_MINUTES])
        refuel_estimate = stove_datetime + time_to_refuel
        nighttime_start = time(hour=data[DATA_NIGHT_BEGIN_HOUR], 
                               minute=data[DATA_NIGHT_BEGIN_MINUTE])
        nighttime_end = time(hour=data[DATA_NIGHT_END_HOUR], 
                             minute=data[DATA_NIGHT_END_MINUTE])
        stove_version = "{}.{}.{}".format(data[DATA_VERSION_MAJOR],
                                          data[DATA_VERSION_MINOR],
                                          data[DATA_VERSION_BUILD])
        remote_version = "{}.{}.{}".format(data[DATA_REMOTE_VERSION_MAJOR],
                                           data[DATA_REMOTE_VERSION_MINOR],
                                           data[DATA_REMOTE_VERSION_BUILD])
        for item in (DATA_STOVE_TEMPERATURE, DATA_ROOM_TEMPERATURE,
                DATA_OXYGEN_LEVEL):
            data[item] = data[item]/100
        processed_data = {
            DATA_ALGORITHM: data[DATA_ALGORITHM],
            DATA_BURN_LEVEL: data[DATA_BURN_LEVEL],
            DATA_MAINTENANCE_ALARMS: data[DATA_MAINTENANCE_ALARMS],
            DATA_MESSAGE_ID: data[DATA_MESSAGE_ID],
            DATA_NEW_FIREWOOD_ESTIMATE: refuel_estimate,
            DATA_NIGHT_BEGIN_TIME: nighttime_start,
            DATA_NIGHT_END_TIME: nighttime_end,
            DATA_NIGHT_LOWERING: data[DATA_NIGHT_LOWERING],
            DATA_OPERATION_MODE: data[DATA_OPERATION_MODE],
            DATA_OXYGEN_LEVEL: data[DATA_OXYGEN_LEVEL],
            DATA_PHASE: phase,
            DATA_REFILL_ALARM: data[DATA_REFILL_ALARM],
            DATA_REMOTE_REFILL_ALARM: data[DATA_REMOTE_REFILL_ALARM],
            DATA_REMOTE_VERSION: remote_version,
            DATA_ROOM_TEMPERATURE: data[DATA_ROOM_TEMPERATURE],
            DATA_SAFETY_ALARMS: data[DATA_SAFETY_ALARMS],
            DATA_STOVE_TEMPERATURE: data[DATA_STOVE_TEMPERATURE],
            DATA_TIME_SINCE_REMOTE_MSG: data[DATA_TIME_SINCE_REMOTE_MSG],
            DATA_DATE_TIME: stove_datetime,
            DATA_TIME_TO_NEW_FIRE_WOOD: time_to_refuel,
            DATA_UPDATING: data[DATA_UPDATING],
            DATA_VALVE1_POSITION: data[DATA_VALVE1_POSITION],
            DATA_VALVE2_POSITION: data[DATA_VALVE2_POSITION],
            DATA_VALVE3_POSITION: data[DATA_VALVE3_POSITION],
            DATA_VERSION: stove_version,
        }
        return processed_data

    async def get_raw_data(self):
        """Request an update from the stove, return raw result."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_DATA_URL)
        data = json.loads(json_str)
        return data

    async def self_test(self, processed=True):
        """Run self test routine, return result dict."""
        if await self._self_test_start():
            values = [
                '',
                'OK',
                'Busy',
                'Skipped',
                ]
            def process_dict(in_dict):
                """Process dict values."""
                if not processed:
                    return in_dict
                out_dict = {}
                for k, v in in_dict.items():
                    out_dict[k] = values[v]
                return out_dict
            while True:
                intermediate_raw = await self._self_test_result()
                if intermediate_raw is None:
                    yield None
                intermediate = process_dict(intermediate_raw)
                yield intermediate
                if not 2 in intermediate_raw.values():
                    break
                await asyncio.sleep(3)
        else:
            yield None

    async def set_burn_level(self, burn_level):
        """Set the desired burnlevel."""
        data = { DATA_LEVEL: burn_level }
        json_str = await self._post('http://' + self.stove_host
                              + STOVE_BURN_LEVEL_URL, data)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_night_lowering(self, state=None):
        """Switch/toggle night lowering (True=on, False=off, None=toggle)."""
        if state is None:
            data = await self.get_raw_data()
            # 0 == Off
            # 2 == On outside night hours
            # 3 == On inside night hours
            # When does night_lowering == 1 happen?
            cur_state = data[DATA_NIGHT_LOWERING] > 0
        else:
            cur_state = not state
        url = (STOVE_NIGHT_LOWERING_OFF_URL if cur_state
               else STOVE_NIGHT_LOWERING_ON_URL)
        json_str = await self._get('http://' + self.stove_host + url)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_night_lowering_hours(self, start=None, end=None):
        """Set night lowering start and end time."""
        if start is None or end is None:
            data = await self.get_data()
        start = start or data[DATA_NIGHT_BEGIN_TIME]
        end = end or data[DATA_NIGHT_END_TIME]
        data = {
            DATA_BEGIN_HOUR: start.hour,
            DATA_BEGIN_MINUTE: start.minute,
            DATA_END_HOUR: end.hour,
            DATA_END_MINUTE: end.minute,
        }
        json_str = await self._post('http://' + self.stove_host
                                    + STOVE_NIGHT_TIME_URL, data)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_remote_refill_alarm(self, state=None):
        """Set or toggle remote_refill_alarm setting."""
        if state is None:
            data = await self.get_raw_data()
            cur_state = data[DATA_REMOTE_REFILL_ALARM] == 1
        else:
            cur_state = not state
        data = { DATA_ENABLE: 0 if cur_state else 1 }
        json_str = await self._post('http://' + self.stove_host
                                   + STOVE_REMOTE_REFILL_ALARM_URL, data)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def set_time(self, new_time=datetime.now()):
        """Set the time and date of the stove."""
        data = {
            'year': new_time.year,
            'month': new_time.month - 1,  # Stove month input is 0 based.
            'day': new_time.day,
            'hours': new_time.hour,
            'minutes': new_time.minute,
            'seconds': new_time.second,
        }
        json_str = await self._post('http://' + self.stove_host
                                    + STOVE_SET_TIME_URL, data)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def start(self):
        """Start the ignition phase."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_START_URL)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def _identify(self):
        """Get identification and set the properties on the object."""

        async def get_name_and_ip():
            """Get stove name and IP."""
            json_str = await self._get('http://' + self.stove_host
                                       + STOVE_ID_URL)
            if json_str is None:
                _LOGGER.warning("Unable to read stove name and IP.")
                return
            stove_id = json.loads(json_str)
            self.name = stove_id[DATA_NAME]
            self.stove_ip = stove_id[DATA_IP]

        async def get_ssid():
            """Get stove SSID."""
            json_str = await self._get('http://' + self.stove_host
                                       + STOVE_ACCESSPOINT_URL)
            if json_str is None:
                _LOGGER.warning("Unable to read stove SSID.")
                return
            stove_ssid = json.loads(json_str)
            self.stove_ssid = stove_ssid[DATA_SSID]

        async def get_version_info():
            """Get stove version info."""
            data = {
                DATA_FILENAME: 'info.xml',
                DATA_MODE: 1
            }
            json_str = await self._post('http://' + self.stove_host
                                        + STOVE_OPEN_FILE_URL, data)
            if json_str is None:
                _LOGGER.warning("Unable to read stove version info.")
                return
            success = json.loads(json_str)
            if success[DATA_SUCCESS] == 1:
                xml_str = await self._post('http://' + self.stove_host
                                           + STOVE_READ_OPEN_FILE_URL, data)
                try:
                    xml_root = ET.fromstring(xml_str)
                    self.full_version = xml_root.find('Name').text
                    self.series = xml_root.find('StoveType').text
                    self.version = xml_root.find('Version').text
                except ET.ParseError:
                    _LOGGER.warning("Invalid XML. Could not get version info.")
                except AttributeError:
                    _LOGGER.warning("Missing key in version info XML.")

        await asyncio.gather(*[
            get_name_and_ip(),
            get_ssid(),
            get_version_info(),
        ])

    async def _self_test_result(self):
        """Get self test result."""
        count = 0
        result = None
        while True:
            # Error prone, retry up to 3 times
            json_str = await self._get('http://' + self.stove_host
                                       + STOVE_SELFTEST_RESULT_URL)
            result = json.loads(json_str)
            if not result.get('reponse'):  # NOT A TYPO!!!
                break
            if count >= 3:
                return
            count = count + 1
            await asyncio.sleep(3)
        return result

    async def _self_test_start(self):
        """Request self test start."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_SELFTEST_START_URL)
        return json.loads(json_str).get(DATA_RESPONSE) == RESPONSE_OK

    async def _get(self, url):
        """Get data from url, return response."""
        try:
            async with self._session.get(url) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error("Could not connect to stove.")

    async def _post(self, url, data):
        """Post data to url, return response."""
        try:
            async with self._session.post(url, data=json.dumps(
                    data, separators=(',', ':'))) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error("Could not connect to stove.")


async def run_command(stove_host, command, value, loop, fast_mode):
    """Run the app with the specified command."""

    async def execute(command, value):
        """Execute the command."""
        if command is None:
            return

        supported_commands = [
            'get_data',
            'get_raw_data',
            'self_test',
            'set_burn_level',
            'set_night_lowering',
            'set_night_lowering_hours',
            'set_remote_refill_alarm',
            'set_time',
            'start',
            ]

        if command not in supported_commands:
            print("Command not supported: {}".format(command))
            return

        if command == 'get_data':
            data = await stv.get_data()
            for k, v in data.items():
                print("{}: {}".format(k, v))
        elif command == 'get_raw_data':
            data = await stv.get_raw_data()
            for k, v in data.items():
                print("{}: {}".format(k, v))
        elif command == 'self_test':
            import math
            async for res in stv.self_test():
                if res is None:
                    print("\nHTTP response timed out.")
                    return

                conf_length = len('Config: {}'.format(
                    res[DATA_TEST_CONFIGURATION]))
                conf_spaces = (15-conf_length) * ' '

                temp_length = len('Temp: {}'.format(
                    res[DATA_TEST_TEMP_SENSOR]))
                temp_spaces = (13-temp_length) * ' '

                o2_length = len('O2: {}'.format(res[DATA_TEST_O2_SENSOR]))
                o2_spaces = (11-o2_length) * ' '

                v1_length = len('Valve1: {}'.format(res[DATA_TEST_VALVE1]))
                v1_spaces = (15-v1_length) * ' '

                v2_length = len('Valve2: {}'.format(res[DATA_TEST_VALVE2]))
                v2_spaces = (15-v2_length) * ' '

                v3_length = len('Valve3: {}'.format(res[DATA_TEST_VALVE3]))
                v3_spaces = (15-v3_length) * ' '

                sys.stdout.write('Config: {}{} | Temp: {}{} | O2: {}{} |'
                                 ' Valve1: {}{} | Valve2: {}{} |'
                                 ' Valve3: {}{}\r'.format(
                                     res[DATA_TEST_CONFIGURATION], conf_spaces,
                                     res[DATA_TEST_TEMP_SENSOR], temp_spaces,
                                     res[DATA_TEST_O2_SENSOR], o2_spaces,
                                     res[DATA_TEST_VALVE1], v1_spaces,
                                     res[DATA_TEST_VALVE2], v2_spaces,
                                     res[DATA_TEST_VALVE3], v3_spaces))
            print()
        elif command == 'set_burn_level':
            try:
                value = int(value)
            except ValueError:
                print("Invalid value: {}".format(value))
                return
            if 0 <= value <= 5:
                if await stv.set_burn_level(value):
                    result = await stv.get_data()
                    if result:
                        print("Burn level set to {}.".format(
                            result[DATA_BURN_LEVEL]))
                    else:
                        print("Unable to confirm success.")
                else:
                    print("Setting burn level failed!")
            else:
                print("Invalid value: {}".format(value))
        elif command == 'set_night_lowering':
            if value is not None:
                value = value.lower() in ('1', 'on')
            if await stv.set_night_lowering(value):
                result = await stv.get_raw_data()
                if result:
                    print("Night lowering switched {}.".format(
                        'on' if result[DATA_NIGHT_LOWERING] else 'off'))
                else:
                    print("Unable to confirm success.")
            else:
                print("Setting night lowering failed.")
        elif command == 'set_night_lowering_hours':
            if value is None:
                print("Value required. Format: <start>-<end>")
                print("<start> and <end> must be in format H[:MM]")
                print("Example: '22-7:30'")
                return
            pat = re.compile(r'^(?P<start_hr>\d+|[01]\d|2[0-3])'
                             '(?::(?P<start_min>[0-5]\d))?-'
                             '(?P<end_hr>\d+|[01]\d|2[0-3])'
                             '(?::(?P<end_min>[0-5]\d))?$')
            match = pat.match(value)
            if not match:
                print("Invalid value format. Expected: <start>-<end>")
                print("<start> and <end> must be in format H[:MM]")
                print("Example: '22-7:30'")
                return
            span = {}
            for k, v in match.groupdict(default=0).items():
                span[k] = int(v)
            start = time(hour=span['start_hr'], minute=span['start_min'])
            end = time(hour=span['end_hr'], minute=span['end_min'])
            if await stv.set_night_lowering_hours(start=start, end=end):
                result = await stv.get_data()
                if result:
                    print("Night lowering hours set.")
                    print("Start: {}".format(result[DATA_NIGHT_BEGIN_TIME]))
                    print("End: {}".format(result[DATA_NIGHT_END_TIME]))
                else:
                    print("Unable to confirm success.")
            else:
                print("Setting night lowering hours failed.")
        elif command == 'set_remote_refill_alarm':
            if value is not None:
                value = value.lower() in ('1', 'on')
            if await stv.set_remote_refill_alarm(value):
                result = await stv.get_raw_data()
                if result:
                    print("Remote refill alarm switched {}.".format(
                        'on' if result[DATA_REMOTE_REFILL_ALARM] else 'off'))
                else:
                    print("Unable to confirm success.")
            else:
                print("Setting remote refill alarm failed.")
        elif command == 'set_time':
            if value is not None:
                try:
                    new_time = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print("Invalid time format: {}".format(value))
                    return
            else:
                new_time = datetime.now()
            if await stv.set_time(new_time):
                result = await stv.get_data()
                if result:
                    print("Stove time set to {}".format(
                        result[DATA_DATE_TIME]))
                else:
                    print("Unable to verify success.")
            else:
                print("Failed to set the time on the stove.")
        elif command == 'start':
            if await stv.start():
                print("Stove ready for start.")
            else:
                print("Stove failed to start.")

    stv = await pystove.create(stove_host, loop, skip_ident=fast_mode)

    print("Stove:\t\t{}".format(stv.name))
    print("Model:\t\t{} Series".format(stv.series))
    print("Host:\t\t{}".format(stv.stove_host))
    print("IP:\t\t{}".format(stv.stove_ip))
    print("SSID:\t\t{}".format(stv.stove_ssid))
    print("Version:\t{}".format(stv.full_version))
    print()

    await execute(command, value)
    await stv.destroy()


if __name__ == '__main__':
    """Handle direct invocation from command line."""
    import getopt

    print("pystove {}".format(__version__))
    print()

    def print_help():
        """Print help message."""
        print("Usage: {} <options>".format(sys.argv[0]))
        print()
        print("Options:")
        print()
        print("  -h, --host <HOST>\t\tRequired")
        print("    The IP address or hostname of the stove.")
        print()
        print("  -f, --fast\t\t\tOptional")
        print("    Run in fast mode (skip ident).")
        print()
        print("  -c, --command <COMMAND>\tOptional")
        print("    The command to send to the stove.")
        print()
        print("  -v, --value <VALUE>\t\tOptional")
        print("    The value to send to the stove with the supplied command.")
        print()
        print()
        print("Supported commands:")
        print()
        print("  get_data")
        print("    Retrieve a list of processed configuration values.")
        print()
        print("  get_raw_data")
        print("    Retrieve a list of unprocessed configuration values.")
        print()
        print("  set_burn_level")
        print("    Set the burn level of the stove.")
        print("    This command requires a value between 0 and 5.")
        print()
        print("  set_night_lowering")
        print("    Set the night lowering option.")
        print("    This command takes an optional value: 1=on, 0=off")
        print("    A call without value toggles the setting.")
        print()
        print("  set_night_lowering_hours")
        print("    Set the night lowering hours on the stove.")
        print("    This command requires a <value> in the form of"
              " <start>-<end>")
        print("    Both <start> and <end> must be in 24h format H[:MM]")
        print()
        print("  set_remote_refill_alarm")
        print("    Set the remote refill alarm.")
        print("    This command takes an optional value: 1=on, 0=off")
        print("    A call without value toggles the setting.")
        print()
        print("   start")
        print("     Set the stove in ignition mode.")
        print()
        print("    set_time")
        print("      Set the time on the stove. Defaults to current"
              " time on this system.")
        print("      Optional value format: YYYY-MM-DD HH:MM:SS")
        print()
        print("    self_test")
        print("      Run stove self test routine and return result.")
        sys.exit()

    command = None
    fast_mode = False
    stove_host = None
    value = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:fh:v:",
                                   ['command=', 'fast', 'host=', 'value='])
    except getopt.GetoptError:
        print_help()
    for opt, arg in opts:
        if opt in ('-c', '--command'):
            command = arg
        elif opt in ('-f', '--fast'):
            fast_mode = True
        elif opt in ('-h', '--host'):
            stove_host = arg
        elif opt in ('-v' '--value'):
            value = arg
    loop = asyncio.get_event_loop()
    if stove_host is None:
        print_help()
    loop.run_until_complete(run_command(stove_host, command, value, loop,
                                        fast_mode))

