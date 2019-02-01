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
import sys
from datetime import datetime, time, timedelta

import aiohttp


DATA_ALGORITHM = 'algorithm'
DATA_BEGIN_HOUR = 'begin_hour'
DATA_BEGIN_MINUTE = 'begin_minute'
DATA_END_HOUR = 'end_hour'
DATA_END_MINUTE = 'end_minute'
DATA_BURN_LEVEL = 'burn_level'
DATA_DATE_TIME = 'date_time'
DATA_IP = 'ip'
DATA_LEVEL = 'level'
DATA_MAINTENANCE_ALARMS = 'maintenance_alarms'
DATA_MESSAGE_ID = 'message_id'
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
DATA_STOVE_TEMPERATURE = 'stove_temperature'
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
    'Ignition phase',
    'Burn phase',
    'Burn phase',
    'Burn phase',
    'Glow phase',
    'Start'
]

RESPONSE_OK = 'OK'

STOVE_BURN_LEVEL_URL = '/set_burn_level'
STOVE_DATA_URL = '/get_stove_data'
STOVE_ID_URL = '/esp/get_identification'
STOVE_NIGHT_LOWERING_OFF_URL = '/set_night_lowering_off'
STOVE_NIGHT_LOWERING_ON_URL = '/set_night_lowering_on'
STOVE_NIGHT_TIME_URL = '/set_night_time'
STOVE_START_URL = '/start'


class pystove():
    """Abstraction of a pystove object."""

    @classmethod
    async def create(cls, stove_host, loop=asyncio.get_event_loop()):
        """Async create the pystove object."""
        self = cls()
        self.stove_host = stove_host
        self.loop = loop
        self._session = aiohttp.ClientSession(headers=HTTP_HEADERS)
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

    async def set_burn_level(self, burn_level):
        """Set the desired burnlevel."""
        data = { DATA_LEVEL: burn_level }
        json_str = await self._post('http://' + self.stove_host
                              + STOVE_BURN_LEVEL_URL, data)
        return json.loads(json_str)[DATA_RESPONSE] == RESPONSE_OK

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
        return json.loads(json_str)[DATA_RESPONSE] == RESPONSE_OK

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
        return json.loads(json_str)[DATA_RESPONSE] == RESPONSE_OK

    async def start(self):
        """Start the ignition phase."""
        json_str = await self._get('http://' + self.stove_host
                                   + STOVE_START_URL)
        return json.loads(json_str)[DATA_RESPONSE] == RESPONSE_OK

    async def _identify(self):
        """Get identification and set the properties on the object."""
        json_str = await self._get('http://' + self.stove_host + STOVE_ID_URL)
        stove_id = json.loads(json_str)
        self.name = stove_id[DATA_NAME]
        self.stove_ip = stove_id[DATA_IP]

    async def _get(self, url):
        """Get data from url, return response."""
        async with self._session.get(url) as response:
            return await response.text()

    async def _post(self, url, data):
        """Post data to url, return response."""
        async with self._session.post(
                url, data=json.dumps(data, separators=(',', ':'))) as response:
            return await response.text()


async def get_data(stove_host, loop=asyncio.get_event_loop()):
    stv = await pystove.create(stove_host, loop)
    print(await stv.get_data())
    await stv.set_night_lowering_hours(start=time(hour=23, minute=30))
    print(await stv.get_data())
    await stv.destroy()

if __name__ == '__main__':
    """Handle direct invocation from command line."""
    stove_host = sys.argv[1]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_data(stove_host, loop))

