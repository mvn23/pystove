# pystove

An async python library with command line interface to interact with HWAM SmartControl wood burning stoves.

### Contents
- [Usage Example](#usage-example)
- [Library Reference](#library-reference)
  - [Properties](#properties)
  - [Methods](#methods)
- [Command Line Invocation](#command-line-invocation)

### Usage Example
```python
import asyncio
from pystove import Stove


HOST = 'stove.local'


async def switch_on_stove():
  """Create a Stove object, switch to ignition mode and set burn level to 5."""

  # Create the object
  stove = await Stove.create(HOST)

  # Switch to ignition mode
  if await stove.start():

    # If successful, set burn level to 5.
    await stove.set_burn_level(5)

  # Clean up
  await stove.destroy()

# Set up the event loop and run the switch_on_stove coroutine.
loop = asyncio.get_event_loop()
loop.run_until_complete(switch_on_stove())

```

## Library Reference

### Properties

#### Stove.algo_version
The algorithm version of the stove.
#### Stove.name
The name of the stove as set during initial configuration.
#### Stove.series
The series/model of the stove.
#### Stove.stove_host
The hostname used during creation of the Stove object.
#### Stove.stove_ip
The IP address as reported by the stove.
#### Stove.stove_mdns
The MAC address prefixed with "ihs_" as reported by the stove.
#### Stove.stove_ssid
The SSID to which the stove is connected.

### Methods

#### @classmethod Stove.create(_cls_, stove_host, loop=asyncio.get_event_loop(), skip_ident=False)
Create a pystove object asynchronously. This method takes the following arguments:

- __stove_host__ The hostname or IP address of the stove.
- __loop__ Event loop to use for the pystove object.
- __skip_ident__ Skip identification calls to the stove. Speeds up creation of the pystove object but the resulting object will be missing its identifying information.

Returns a pystove object with at least the `stove_host` property set. If `skip_ident` was set to `False` (the default), all other properties should be set as well

This method is a coroutine.

#### Stove.destroy(_self_)
Run a cleanup of the Stove object. This method should be called before exiting your program to avoid error messages.

This method is a coroutine.

#### Stove.get_data(_self_)
Retrieve information about the current state of the stove.
Returns a dict containing processed information about the current state of the stove. Useful for e.g. display purposes as most variables have been processed into readable information or python data types.

This method is a coroutine.

#### Stove.get_live_data(_self_)
Retrieve a log of recent temperature and oxygen level data from the stove.
Returns a dict with the following structure:
```python
{
  pystove.DATA_STOVE_TEMPERATURE: [...],
  pystove.DATA_OXYGEN_LEVEL: [...]
}
```
Each item contains a sequential list with historical sensor data for each minute of the last 2 hours.

This method is a coroutine.

#### Stove.get_raw_data(_self_)
Retrieve information about the current state of the stove.
Returns a dict containing unprocessed information about the current state of the stove. All information is forwarded as provided by the stove.

This method is a coroutine.

#### Stove.self_test(_self_, processed=True)
Start and monitor the self-test routine of the stove. This method will request and return intermediate results every 3 seconds until all tests have either been passed or skipped.
The following argument is supported:

- __processed__ Whether the results should be processed into human-readable form. Defaults to `True`.

This method is a generator coroutine.

#### Stove.set_burn_level(_self_, burn_level)
Set the burn level on the stove. Returns `True` on success.
This method takes the following argument:

- __burn_level__ The burn level to set on the stove. Supported values are 0 through 5.

This method is a coroutine.

#### Stove.set_night_lowering(_self_, state=None)
Set or toggle the night lowering option on the stove. Returns `True` on success.
This method takes the following argument:

- __state__ The new night lowering setting to set on the stove. Supported values must evaluate to `True` or `False`. If omitted or `None` (the default), the setting will be toggled.

This method is a coroutine.

#### Stove.set_night_lowering_hours(_self_, start=None, end=None)
Set the night lowering hours on the stove. Returns `True` on success.
This method takes the following arguments:

- __start__ A `datetime.time` object containing the requested night lowering start time. If omitted or `None`, the start time will not be changed.
- __end__ A `datetime.time` object containing the requested night lowering end time. If omitted or `None`, the end time will not be changed.

This method is a coroutine.

#### Stove.set_remote_refill_alarm(_self_, state=None)
Set the remote refill alarm. Returns `True` on success.
This method takes the following argument:

- __state__ The new remote refill alarm setting to set on the stove. Supported values must evaluate to `True` or `False`. If omitted or `None` (the default), the setting will be toggled.

This method is a coroutine.

#### Stove.set_time(_self_, new_time=datetime.now())
Set the time and date on the stove. Returns `True` on success.
This method takes the following argument:

- __new_time__ A `datetime.datetime` object containing the time and date to set on the stove. If omitted, the current time on the local host will be used.

This method is a coroutine.

#### Stove.start(_self_)
Switch the stove to `Ignition` mode. Returns `True` on success.

This method is a coroutine.

## Command Line Invocation
```
Usage: ./pystove_cli.py <options>

Options:

  -h, --host <HOST>		Required
    The IP address or hostname of the stove.

  -f, --fast			Optional
    Run in fast mode (skip ident).

  -c, --command <COMMAND>	Optional
    The command to send to the stove.
    If no command is provided, it defaults to show_info.

  -v, --value <VALUE>		Optional
    The value to send to the stove with the supplied command.


Supported commands:

  get_data
    Retrieve a list of processed configuration values.

  get_live_data:
    Retrieve historical stove temperature and oxygen level
    data from the last 2 hours.

  get_raw_data
    Retrieve a list of unprocessed configuration values.

  self_test
    Run stove self test routine and return result.

  set_burn_level
    Set the burn level of the stove.
    This command requires a value between 0 and 5.

  set_night_lowering
    Set the night lowering option.
    This command takes an optional value: 1=on, 0=off
    A call without value toggles the setting.

  set_night_lowering_hours
    Set the night lowering hours on the stove.
    This command requires a <value> in the form of <start>-<end>
    Both <start> and <end> must be in 24h format H[:MM]

  set_remote_refill_alarm
    Set the remote refill alarm.
    This command takes an optional value: 1=on, 0=off
    A call without value toggles the setting.

  set_time
    Set the time on the stove. Defaults to current time on this system.
    Optional value format: YYYY-MM-DD HH:MM:SS

  show_info
    Show the stove identification information.

  start
    Set the stove in ignition mode.

```
