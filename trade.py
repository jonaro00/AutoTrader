#!/usr/bin/env python3
"""
AutoTrader, a script for automating trading in Pokémon GO on Android.
Author: jonaro00
"""

import asyncio
from dataclasses import dataclass
import time
from pathlib import Path

try:
    from ppadb.client_async import ClientAsync
    from ppadb.device_async import DeviceAsync
    import yaml
    from yaml.parser import ParserError
except ModuleNotFoundError as e:
    print(e)
    print('Run "pip install -r requirements.txt" to install required packages.')
    exit(1)

CONFIG_FILE_DIR  = '/storage/self/primary/'
CONFIG_FILE_NAME = 'AutoTraderConfig.yaml'
TMP_FILE_PATH    = Path('tmp.yaml')
CONFIG = dict[str, list[int]]


@dataclass
class Button:
    name: str
    delay_after: float
    use_delay_modifier: bool


BUTTONS = [
    Button(
        'TRADE_BTN',
        6,
        True,
    ),
    Button(
        'FIRST_PKMN_BTN',
        1,
        False,
    ),
    Button(
        'NEXT_BTN',
        4,
        True,
    ),
    Button(
        'CONFIRM_BTN',
        15,
        True,
    ),
    Button(
        'X_BTN',
        1,
        False,
    ),
]
BUTTON_NAMES = set(btn.name for btn in BUTTONS)
SLEEP_MODIFIER = 0


class DeviceAsyncWrapper(DeviceAsync):
    config: CONFIG


class AutoTraderError(Exception):
    pass


async def tap(device: DeviceAsyncWrapper, point: list[int]):
    """Sends a tap at point to device."""
    x, y = point
    # Uses a tiny swipe over 100 ms for increased reliability
    # and visibility on the Pointer Location tool.
    await device.shell(f'input swipe {x} {y} {x+1} {y+1} 100')


async def trade_sequence(devices: list[DeviceAsyncWrapper]):
    """Sends taps to devices in a sequence with delays
    to complete a trade process. Device must have
    button coordinates stored in attribute `config`."""
    global SLEEP_MODIFIER
    for btn in BUTTONS:
        delay = max(btn.delay_after + (SLEEP_MODIFIER if btn.use_delay_modifier else 0), 0)
        commands = (tap(dev, dev.config[btn.name]) for dev in devices)
        print('    Sending', btn.name)
        await asyncio.gather(*commands)
        await asyncio.sleep(delay)


async def trade_process(devices: list[DeviceAsyncWrapper], n_trades: int):
    """Executes `n_trades` trading sequences."""
    if n_trades < 1:
        return
    await pointer(devices, True)
    try:
        for i in range(1, n_trades+1):
            print(f'  Starting trade {i} of {n_trades}')
            await trade_sequence(devices)
    finally:
        await pointer(devices, False)


async def get_config(device: DeviceAsyncWrapper) -> CONFIG:
    """Pulls config file from device and parses it. Sets the `config` attribute on success."""
    config_file_path = CONFIG_FILE_DIR + CONFIG_FILE_NAME
    await device.pull(config_file_path, TMP_FILE_PATH)
    content = TMP_FILE_PATH.read_text()
    TMP_FILE_PATH.unlink()
    if not content:
        raise AutoTraderError(f'Found no config file at {config_file_path}')
    config: CONFIG = yaml.safe_load(content)
    assert isinstance(config, dict), f'Incorrect config file format (should be an object with keys)'
    if not BUTTON_NAMES <= set(config.keys()):
        raise AutoTraderError(f'Missing config key(s): {BUTTON_NAMES - set(config.keys())}')
    for coords in config.values():
        assert isinstance(coords, list) and all(map(lambda i: isinstance(i, int), coords)),\
            f'Invalid coords format in config (should be list with two integers)'
    device.config = config
    return config


async def set_setting(device: DeviceAsyncWrapper, namespace_and_key: str, value):
    """Wraps 'settings put' in adb shell. Sets key in namespace to value."""
    await device.shell(f'settings put {namespace_and_key} {value}')


async def pointer(devices: list[DeviceAsyncWrapper], on: bool):
    """Turns on/off pointer location setting on all `devices`."""
    for device in devices:
        try:
            await set_setting(device, 'system pointer_location', int(on))
        except Exception:
            print(f'Failed to turn {"on" if on else "off"} pointer location on', device.serial)


async def setup() -> list[DeviceAsyncWrapper]:
    """Checks for devices and loads config files from devices."""
    client = ClientAsync()
    devices: list[DeviceAsyncWrapper] = await client.devices()
    if not devices:
        raise AutoTraderError('No devices found')
    print('Found devices:')
    for device in devices:
        print(' ', device.serial)
    print()
    try:
        for device in devices:
            await get_config(device)
            print('Successfully loaded config from', device.serial)
    except (AutoTraderError, AssertionError, ParserError) as e:
        raise AutoTraderError(f'Failed to load config from {device.serial}', *e.args) from e
    return devices


def interface():
    """Runs the main loop asking for user input."""
    global SLEEP_MODIFIER
    print(
        '\n'
        ' ##                          ## \n'
        '##   AutoTrader by jonaro00   ##\n'
        ' ##                          ## \n'
    )
    devices: list[DeviceAsyncWrapper] = asyncio.run(setup())
    while True:
        print()
        try:
            i = input("Number of trades? ('q' to quit) > ").strip()
            il = i.lower()
            if il == 'q':
                break
            if il.startswith('delay'):
                args = i.split()
                args_l = len(args)
                if args_l == 2:
                    SLEEP_MODIFIER = float(args[1])
                print('Current extra delay:', SLEEP_MODIFIER)
                continue
            assert (n := int(i)) > 0
        except KeyboardInterrupt:
            print('\nDouble press interrupt to quit')
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                break
            continue
        except EOFError:
            break
        except (ValueError, AssertionError):
            print('Enter a positive integer')
            continue
        try:
            print(f'Starting {n} trades (Ctrl+C to cancel)...')
            asyncio.run(trade_process(devices, n))
        except KeyboardInterrupt:
            continue
        except Exception as e:
            print(e)


def main():
    try:
        interface()
    except AutoTraderError as e:
        print('\n'.join(map(str, e.args)))
    except Exception as e:
        print('Unexpected error:', e.__class__.__name__, e.args)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

# https://github.com/encode/httpx/issues/914#issuecomment-622586610
# https://github.com/aio-libs/aiohttp/issues/4324
# https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349
