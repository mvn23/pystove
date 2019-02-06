#!/usr/bin/env python3

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

import asyncio
import re
import sys

from datetime import datetime, time


from pystove.pystove import (
    DATA_TEST_CONFIGURATION, DATA_TEST_O2_SENSOR, DATA_TEST_TEMP_SENSOR,
    DATA_TEST_VALVE1, DATA_TEST_VALVE2, DATA_TEST_VALVE3, DATA_BURN_LEVEL,
    DATA_NIGHT_LOWERING, DATA_NIGHT_BEGIN_TIME, DATA_NIGHT_END_TIME,
    DATA_REMOTE_REFILL_ALARM, DATA_DATE_TIME, Stove
    )
from pystove.version import __version__


async def run_command(stove_host, command, value, loop):
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
            'show_info',
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
        elif command == 'show_info':
            print("pystove {}".format(__version__))
            print()
            print("Stove:\t\t{}".format(stv.name))
            print("Model:\t\t{} Series".format(stv.series))
            print("Host:\t\t{}".format(stv.stove_host))
            print("IP:\t\t{}".format(stv.stove_ip))
            print("SSID:\t\t{}".format(stv.stove_ssid))
            print("Algo Version:\t{}".format(stv.algo_version))
            print()
        elif command == 'start':
            if await stv.start():
                print("Stove ready for start.")
            else:
                print("Stove failed to start.")
	
    stv = await Stove.create(stove_host, loop, 
                             skip_ident=command != 'show_info')
    await execute(command, value)
    await stv.destroy()


if __name__ == '__main__':
    """Handle direct invocation from command line."""
    import getopt

    def print_help():
        """Print help message."""
        print("Usage: {} <options>".format(sys.argv[0]))
        print()
        print("Options:")
        print()
        print("  -h, --host <HOST>\t\tRequired")
        print("    The IP address or hostname of the stove.")
        print()
        print("  -c, --command <COMMAND>\tOptional")
        print("    The command to send to the stove.")
        print("    If no command is provided, it defaults to show_info.")
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
        print("  self_test")
        print("    Run stove self test routine and return result.")
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
        print("  set_time")
        print("    Set the time on the stove. Defaults to current"
              " time on this system.")
        print("    Optional value format: YYYY-MM-DD HH:MM:SS")
        print()
        print("  show_info")
        print("    Show the stove identification information.")
        print()
        print("  start")
        print("    Set the stove in ignition mode.")
        print()

        sys.exit()

    command = 'show_info'
    stove_host = None
    value = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:h:v:",
                                   ['command=', 'host=', 'value='])
    except getopt.GetoptError:
        print_help()
    for opt, arg in opts:
        if opt in ('-c', '--command'):
            command = arg
        elif opt in ('-h', '--host'):
            stove_host = arg
        elif opt in ('-v' '--value'):
            value = arg
    if stove_host is None:
        print_help()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_command(stove_host, command, value, loop))

