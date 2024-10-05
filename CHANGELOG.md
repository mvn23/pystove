# pystove Changelog

###
- Add CHANGELOG.md
- Add vscode devcontainer setup and dependabot config (#2) (thanks @lordyavin)
- Add support for reading the MDNS (#1) (thanks @lordyavin)
- Improve reading of identification data (thanks @lordyavin)
- Rename get_name_and_ip() to get_identification (thanks @lordyavin)
- Implement pystove._get_json

### 0.2a1
- Update self_test for backwards compatibility with python3.5
- Improve error handling (empty or no response)

### 0.2a0
- Update setup.py to reflect new name for README.md.
- Fix bug with empty response in Stove._identify() and Stove.self_test()
- Rename DATA_VERSION* to DATA_FIRMWARE_VERSION*
- Update .gitignore
- Update imports in __init__.py
- Rename FIRE_WOOD vars to FIREWOOD for consistency
- Add Stove.get_live_data() coroutine for historical data
- Implement get_live_data on CLI
- Improve CLI formatting for self test results
- Rename 'Start' phase to 'Standby'
- Update self test result values/strings
- Translate maintenance alarms, safety alarms, operation mode and night lowering to strings in Stove.get_data
- Make stove temperature, room temperature and oxygen level an int in get_data and get_raw_data as they would always end in .00
- fix Usage Example in README.md
- flake8 fixes
- Update CLI workflow.
- Remove fast_mode option in favour of show_info command
- Update help and README.md
- Improve version naming
- Do not show list with empty values in fast mode
- Rename pystove class to Stove
- Move CLI to dedicated pystove_cli.py file in root dir
- Add license header to version.py

### 0.1a0
- Implement self test
- Implement set_time
- Implement CLI
- Add logging and error handling
- Implement set_remote_refill_alarm
- Implement start, night_lowering and night_lowering_hours
- Add HTTP post functionality
- Implement set_burn_level (untested)
- Implement basic data fetch functionality
