#!/usr/bin/python3

"""
AutoTrader, a script for automating trading in Pokémon GO on Android.
Author: jonaro00
"""

import asyncio
import json
from json.decoder import JSONDecodeError
import time

from ppadb.client_async import ClientAsync
from ppadb.device_async import DeviceAsync


CONFIG_FILE_DIR  = '/storage/self/primary/'
CONFIG_FILE_NAME = 'AutoTraderConfig.json'
TMP_FILE_PATH    = 'tmp.json'

BUTTON_COORDS = ('TRADE_BTN', 'FIRST_PKMN_BTN', 'NEXT_BTN', 'CONFIRM_BTN', 'X_BTN')
SLEEP_DELAYS  = (7, 1, 5, 21, 1)


async def tap(device: DeviceAsync, point: 'tuple[int, int]') -> None:
    """Sends a tap at point to device."""
    x, y = point
    # Uses a tiny swipe over 100 ms for increased reliability
    # and visibility on the Pointer Location tool.
    await device.shell(f'input swipe {x} {y} {x+1} {y+1} 100')


async def trade_sequence(devices: 'list[DeviceAsync]') -> None:
    """Sends taps to devices in a sequence with delays
    to complete a trade process. Device must have
    button coordinates stored in attribute 'conf'."""
    for btn, delay in zip(BUTTON_COORDS, SLEEP_DELAYS):
        commands = (tap(dev, dev.conf[btn]) for dev in devices)
        print('    Sending', btn)
        await asyncio.gather(*commands)
        time.sleep(delay)
        # await asyncio.sleep(delay)


async def trade_process(devices: 'list[DeviceAsync]', n_trades: int, total: int) -> int:
    """Executes `n_trades` trading sequences. Returns number of trades completed."""
    if n_trades < 1:
        return 0
    await pointer(devices, True)
    try:
        for i in range(1, n_trades+1):
            print(f'  Starting trade {i} of {n_trades} ({total+i} total)')
            await trade_sequence(devices)
        i += 1
    finally:
        await pointer(devices, False)
        return i-1


async def get_config(device: DeviceAsync) -> 'dict[str, list[int, int]]':
    """Pulls config file from device and parses it. Sets the `conf` attribute on success."""
    config_file_path = CONFIG_FILE_DIR + CONFIG_FILE_NAME
    await device.pull(config_file_path, TMP_FILE_PATH)
    with open(TMP_FILE_PATH, 'rb') as f:
        if f.read(1) == b'':
            raise LookupError(f'Found no config file at {config_file_path}')
        f.seek(0, 0)
        try:
            conf = json.load(f)
        except JSONDecodeError as e:
            raise ValueError(f'Error while parsing config file {config_file_path}') from e
    assert isinstance(conf, dict), f'Incorrect config file format (should be an object with keys)'
    if not set(BUTTON_COORDS) <= set(conf.keys()):
        raise KeyError(f'Missing config key(s): {set(BUTTON_COORDS) - set(conf.keys())}')
    for coords in conf.values():
        assert isinstance(coords, list) and all(map(lambda i: isinstance(i, int), coords)),\
            f'Invalid coords format in config (should be list with two integers)'
    device.conf = conf
    return conf


async def set_setting(device: DeviceAsync, namespace_and_key: str, value) -> None:
    """Wraps 'settings put' in adb shell. Sets key in namespace to value."""
    await device.shell(f'settings put {namespace_and_key} {value}')


async def pointer(devices: 'list[DeviceAsync]', on: bool) -> None:
    """Turns on/off pointer location setting on all `devices`."""
    for device in devices:
        try:
            await set_setting(device, 'system pointer_location', int(on))
        except Exception:
            print(f'Failed to turn {"on" if on else "off"} pointer location on', device.serial)


async def setup() -> 'list[DeviceAsync]':
    """Checks for devices and loads config files from devices."""
    client = ClientAsync()
    devices: list[DeviceAsync] = await client.devices()
    if not devices:
        raise RuntimeError('No devices found')
    print('Found devices:')
    for device in devices:
        print(' ', device.serial)
    print()
    try:
        for device in devices:
            await get_config(device)
            print('Successfully loaded config from', device.serial)
    except Exception as e:
        raise RuntimeError(f'Failed to load config from {device.serial}:', *e.args)
    return devices


async def interface() -> None:
    """Runs the main loop asking for user input."""
    devices: list[DeviceAsync] = await setup()
    total = 0
    while True:
        print()
        try:
            if total:
                print(f'[{total} total]')
            i = input("Number of trades? ('q' to quit) > ")
            if i in ('q', 'Q'):
                break
            n = int(i)
        except KeyboardInterrupt:
            print('\nDouble press interrupt to quit')
            time.sleep(0.5)
            continue
        except EOFError:
            break
        except ValueError:
            print('Enter a positive integer')
            continue
        try:
            print(f'Starting {n} trades (Ctrl+C to cancel)...')
            total += await trade_process(devices, n, total)
        except KeyboardInterrupt:
            continue
        except Exception as e:
            print(e)


def main() -> None:
    print()
    print(' ##                          ## ')
    print('##   AutoTrader by jonaro00   ##')
    print(' ##                          ## ')
    print()
    try:
        asyncio.run(interface())
    except RuntimeError as e:
        print('\n'.join(e.args))
        return
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()

# https://github.com/encode/httpx/issues/914#issuecomment-622586610
# https://github.com/aio-libs/aiohttp/issues/4324
# https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349
