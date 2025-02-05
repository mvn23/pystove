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
from datetime import datetime, time, timedelta
import re
import sys

from pystove.pystove import (
    DATA_BURN_LEVEL,
    DATA_DATE_TIME,
    DATA_NIGHT_BEGIN_TIME,
    DATA_NIGHT_END_TIME,
    DATA_NIGHT_LOWERING,
    DATA_OXYGEN_LEVEL,
    DATA_REMOTE_REFILL_ALARM,
    DATA_STOVE_TEMPERATURE,
    DATA_TEST_CONFIGURATION,
    DATA_TEST_O2_SENSOR,
    DATA_TEST_TEMP_SENSOR,
    DATA_TEST_VALVE1,
    DATA_TEST_VALVE2,
    DATA_TEST_VALVE3,
    Stove,
)
from pystove.version import __version__


async def run_command(stove_host, command, value):
    """Run the app with the specified command."""

    async def execute(command, value):
        """Execute the command."""
        if command is None:
            return

        supported_commands = [
            "get_data",
            "get_live_data",
            "get_raw_data",
            "self_test",
            "set_burn_level",
            "set_night_lowering",
            "set_night_lowering_hours",
            "set_remote_refill_alarm",
            "set_time",
            "show_info",
            "start",
        ]

        if command not in supported_commands:
            print(f"Command not supported: {command}")
            return

        if command == "get_data":
            data = await stv.get_data()
            for k, v in data.items():
                print(f"{k}: {v}")
        elif command == "get_live_data":
            data = await stv.get_live_data()
            point_in_time = datetime.now() - timedelta(minutes=120)
            minute = timedelta(minutes=1)
            print("Time\tTemperature\tOxygen")
            for i in range(120):
                print(
                    "{}\t{:11.2f}\t{:6.2f}".format(
                        point_in_time.strftime("%H:%M"),
                        data[DATA_STOVE_TEMPERATURE][i],
                        data[DATA_OXYGEN_LEVEL][i],
                    )
                )
                point_in_time = point_in_time + minute
        elif command == "get_raw_data":
            data = await stv.get_raw_data()
            for k, v in data.items():
                print(f"{k}: {v}")
        elif command == "self_test":
            async for res in stv.self_test():
                if res is None:
                    print("\nHTTP response timed out.")
                    return
                sys.stdout.write(
                    f"Config: {res[DATA_TEST_CONFIGURATION]:13}"
                    f" | Temp: {res[DATA_TEST_TEMP_SENSOR]:13}"
                    f" | O2: {res[DATA_TEST_O2_SENSOR]:13}"
                    f" | Valve1: {res[DATA_TEST_VALVE1]:13}"
                    f" | Valve2: {res[DATA_TEST_VALVE2]:13}"
                    f" | Valve3: {res[DATA_TEST_VALVE3]:13}"
                    f"\r"
                )
            print()
        elif command == "set_burn_level":
            try:
                value = int(value)
            except ValueError:
                print(f"Invalid value: {value}")
                return
            if 0 <= value <= 5:
                if await stv.set_burn_level(value):
                    result = await stv.get_data()
                    if result:
                        print(f"Burn level set to {result[DATA_BURN_LEVEL]}.")
                    else:
                        print("Unable to confirm success.")
                else:
                    print("Setting burn level failed!")
            else:
                print(f"Invalid value: {value}")
        elif command == "set_night_lowering":
            if value is not None:
                value = value.lower() in ("1", "on")
            if await stv.set_night_lowering(value):
                result = await stv.get_raw_data()
                if result:
                    print(
                        "Night lowering switched {}.".format(
                            "on" if result[DATA_NIGHT_LOWERING] else "off"
                        )
                    )
                else:
                    print("Unable to confirm success.")
            else:
                print("Setting night lowering failed.")
        elif command == "set_night_lowering_hours":
            if value is None:
                print("Value required. Format: <start>-<end>")
                print("<start> and <end> must be in format H[:MM]")
                print("Example: '22-7:30'")
                return
            pat = re.compile(
                r"^(?P<start_hr>\d+|[01]\d|2[0-3])"
                r"(?::(?P<start_min>[0-5]\d))?-"
                r"(?P<end_hr>\d+|[01]\d|2[0-3])"
                r"(?::(?P<end_min>[0-5]\d))?$"
            )
            match = pat.match(value)
            if not match:
                print("Invalid value format. Expected: <start>-<end>")
                print("<start> and <end> must be in format H[:MM]")
                print("Example: '22-7:30'")
                return
            span = {}
            for k, v in match.groupdict(default=0).items():
                span[k] = int(v)
            start = time(hour=span["start_hr"], minute=span["start_min"])
            end = time(hour=span["end_hr"], minute=span["end_min"])
            if await stv.set_night_lowering_hours(start=start, end=end):
                result = await stv.get_data()
                if result:
                    print("Night lowering hours set.")
                    print(f"Start: {result[DATA_NIGHT_BEGIN_TIME]}")
                    print(f"End: {result[DATA_NIGHT_END_TIME]}")
                else:
                    print("Unable to confirm success.")
            else:
                print("Setting night lowering hours failed.")
        elif command == "set_remote_refill_alarm":
            if value is not None:
                value = value.lower() in ("1", "on")
            if await stv.set_remote_refill_alarm(value):
                result = await stv.get_raw_data()
                if result:
                    print(
                        "Remote refill alarm switched {}.".format(
                            "on" if result[DATA_REMOTE_REFILL_ALARM] else "off"
                        )
                    )
                else:
                    print("Unable to confirm success.")
            else:
                print("Setting remote refill alarm failed.")
        elif command == "set_time":
            if value is not None:
                try:
                    new_time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print(f"Invalid time format: {value}")
                    return
            else:
                new_time = datetime.now()
            if await stv.set_time(new_time):
                result = await stv.get_data()
                if result:
                    print(f"Stove time set to {result[DATA_DATE_TIME]}")
                else:
                    print("Unable to verify success.")
            else:
                print("Failed to set the time on the stove.")
        elif command == "show_info":
            print(f"pystove {__version__}")
            print()
            print(f"Stove:\t\t{stv.name}")
            print(f"Model:\t\t{stv.series} Series")
            print(f"Host:\t\t{stv.stove_host}")
            print(f"IP:\t\t{stv.stove_ip}")
            print(
                "MAC:\t\t"
                + ":".join(
                    [f"{stv.mac_address:012x}"[i : i + 2] for i in range(0, 12, 2)]
                )
            )
            print(f"MDNS:\t\t{stv.stove_mdns}")
            print(f"SSID:\t\t{stv.stove_ssid}")
            print(f"Algo Version:\t{stv.algo_version}")
            print()
        elif command == "start":
            if await stv.start():
                print("Stove ready for start.")
            else:
                print("Stove failed to start.")

    stv = await Stove.create(stove_host, skip_ident=command != "show_info")
    await execute(command, value)
    await stv.destroy()


if __name__ == "__main__":
    """Handle direct invocation from command line."""
    import getopt

    def print_help():
        """Print help message."""
        print(f"Usage: {sys.argv[0]} <options>")
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
        print("  get_live_data:")
        print("    Retrieve historical stove temperature and oxygen level")
        print("    data from the last 2 hours.")
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
        print("    This command requires a <value> in the form of <start>-<end>")
        print("    Both <start> and <end> must be in 24h format H[:MM]")
        print()
        print("  set_remote_refill_alarm")
        print("    Set the remote refill alarm.")
        print("    This command takes an optional value: 1=on, 0=off")
        print("    A call without value toggles the setting.")
        print()
        print("  set_time")
        print("    Set the time on the stove. Defaults to current time on this system.")
        print("    Optional value format: YYYY-MM-DD HH:MM:SS")
        print()
        print("  show_info")
        print("    Show the stove identification information.")
        print()
        print("  start")
        print("    Set the stove in ignition mode.")
        print()

        sys.exit()

    command = "show_info"
    stove_host = None
    value = None
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "c:h:v:", ["command=", "host=", "value="]
        )
    except getopt.GetoptError:
        print_help()
    for opt, arg in opts:
        if opt in ("-c", "--command"):
            command = arg
        elif opt in ("-h", "--host"):
            stove_host = arg
        elif opt in ("-v", "--value"):
            value = arg
    if stove_host is None:
        print_help()
    asyncio.run(run_command(stove_host, command, value))
