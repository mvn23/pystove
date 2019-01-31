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

import aiohttp


STOVE_BURN_LEVEL_URL = '/set_burn_level'
STOVE_DATA_URL = '/get_stove_data'
STOVE_ID_URL = '/esp/get_identification'

DATA_UPDATING = 'updating'
DATA_MESSAGE_ID = 'message_id'
DATA_PHASE = 'phase'
DATA_NIGHT_LOWERING = 'night_lowering'
DATA_NEW_FIREWOOD_HOURS = 'new_fire_wood_hours'
DATA_NEW_FIREWOOD_MINUTES = 'new_fire_wood_minutes'
DATA_BURN_LEVEL = 'burn_level'
DATA_OPERATION_MODE = 'operation_mode'
DATA_MAINTENANCE_ALARMS = 'maintenance_alarms'
DATA_SAFETY_ALARMS = 'safety_alarms'
DATA_REFILL_ALARM = 'refill_alarm'
DATA_REMOTE_REFILL_ALARM = 'remote_refill_alarm'
DATA_TIME_SINCE_REMOTE_MSG = 'time_since_remote_msg'
DATA_VERSION_MAJOR = 'version_major'
DATA_VERSION_MINOR = 'version_minor'
DATA_VERSION_BUILD = 'version_build'
DATA_REMOTE_VERSION_MAJOR = 'remote_version_major'
DATA_REMOTE_VERSION_MINOR = 'remote_version_minor'
DATA_REMOTE_VERSION_BUILD = 'remote_version_build'
DATA_DAY = 'day'
DATA_MONTH = 'month'
DATA_YEAR = 'year'
DATA_HOURS = 'hours'
DATA_MINUTES = 'minutes'
DATA_SECONDS = 'seconds'
DATA_NIGHT_BEGIN_HOUR = 'night_begin_hour'
DATA_NIGHT_BEGIN_MINUTE = 'night_begin_minute'
DATA_NIGHT_END_HOUR = 'night_end_hour'
DATA_NIGHT_END_MINUTE = 'night_end_minute'
DATA_STOVE_TEMPERATURE = 'stove_temperature'
DATA_ROOM_TEMPERATURE = 'room_temperature'
DATA_OXYGEN_LEVEL = 'oxygen_level'
DATA_VALVE1_POSITION = 'valve1_position'
DATA_VALVE2_POSITION = 'valve2_position'
DATA_VALVE3_POSITION = 'valve3_position'
DATA_ALGORITHM = 'algorithm'

PHASE = [
    'Ignition phase',
    'Burn phase',
    'Burn phase',
    'Burn phase',
    'Glow phase',
    'Start'
]


class pystove():
    """Abstraction of a pystove object."""

    @classmethod
    async def create(cls, stove_ip, loop=asyncio.get_event_loop()):
        """Async create the pystove object."""
        self = cls()
        self.stove_ip = stove_ip
        self.loop = loop
        return self

    async def get_data(self):
        """Call get_raw_data, process result before returning."""
        data = await self.get_raw_data()
        # TODO process data
        return data

    async def get_raw_data(self):
        """Request an update from the stove, return raw result."""
        async with aiohttp.ClientSession() as session:
            json_str = await self._fetch(session, 'http://' + self.stove_ip
                                         + STOVE_DATA_URL)
            data = json.loads(json_str)
            return data

    @staticmethod
    async def _fetch(session, url):
        """Fetch url, return response."""
        async with session.get(url) as response:
            return await response.text()
        
        
async def get_data(stove_ip, loop=asyncio.get_event_loop()):
    stv = await pystove.create(stove_ip, loop)
    data = await stv.get_data()
    print(json.dumps(data, indent=1))

if __name__ == '__main__':
    """Handle direct invocation from command line."""
    stove_ip = sys.argv[1]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_data(stove_ip, loop))

