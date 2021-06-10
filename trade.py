import asyncio
import json
import sys
from time import sleep

from ppadb.client_async import ClientAsync


CONFIG_FILE_DIR  = '/storage/self/primary/'
CONFIG_FILE_NAME = 'AutoTraderConfig.json'
TMP_FILE_PATH    = 'tmp.json'

BUTTON_COORDS = ('TRADE_BTN', 'FIRST_PKMN_BTN', 'NEXT_BTN', 'CONFIRM_BTN', 'X_BTN')
SLEEP_DELAYS  = (4, 2, 2, 19, 1)

async def tap(dev, point):
    """Sends a tap at point to device."""
    x, y = point
    x2, y2 = x+1, y+1
    cmd = f'input swipe {x} {y} {x2} {y2} 100'
    await dev.shell(cmd)

async def trade_sequence(devs):
    """Sends taps to devices in a sequence with delays
    to complete a trade process. Device must have
    button coordinates stored in attribute 'conf'."""
    for btn, delay in zip(BUTTON_COORDS, SLEEP_DELAYS):
        commands = (tap(dev, dev.conf[btn]) for dev in devs)
        print('  Sending', btn)
        await asyncio.gather(*commands)
        sleep(delay)

async def get_config(device):
    """Pulls config file from device and parses it.
    Sets the 'conf' attribute on success."""
    config_file_path = CONFIG_FILE_DIR + CONFIG_FILE_NAME
    await device.pull(config_file_path, TMP_FILE_PATH)
    with open(TMP_FILE_PATH, 'rb') as f:
        try:
            conf = json.load(f)
        except Exception as e:
            raise LookupError(f'Found no config file ({config_file_path})') from e
        if not set(BUTTON_COORDS) <= set(conf.keys()):
            raise KeyError(
                f'Missing config key(s):\nRequired: {BUTTON_COORDS}\nFound:    {tuple(conf.keys())}'
                )
        try:
            for coords in conf.values():
                assert isinstance(coords[0], int)
                assert isinstance(coords[1], int)
        except Exception as e:
            raise TypeError(
                f'Invalid coords format in config (should be list of two integers):\n{conf}'
                ) from e

        device.conf = conf

async def set_setting(device, namespace_and_key, value):
    """Wraps 'settings put' in adb shell. Sets key in namespace to value."""
    await device.shell(f'settings put {namespace_and_key} {value}')

async def trade_process(n_trades):
    """Checks for devices, loads config files from devices,
    turns on pointer location, and executes n_trades trading sequences."""
    # Setup & device check
    client = ClientAsync()
    devices = await client.devices()
    if not devices:
        print('No devices found')
        return
    print('Found devices:')
    for device in devices:
        print(device.serial)
    print()

    # Config loading
    try:
        for device in devices:
            await get_config(device)
            print('Successfully loaded config from', device.serial)
    except Exception as e:
        print(f'Failed to load config from {device.serial}:')
        print(*e.args)
        return

    input(f'\nPress Enter to start {n_trades} trades (Ctrl+C to cancel)...')

    # Turn on pointer
    for device in devices:
        try:
            await set_setting(device, 'system pointer_location', 1)
        except Exception:
            print('Failed to turn on pointer location on', device.serial)

    # Trade sequence
    try:
        for i in range(1, n_trades+1):
            print('Starting trade', i)
            await trade_sequence(devices)
    except BaseException as e:
        # Turn off pointer
        for device in devices:
            try:
                await set_setting(device, 'system pointer_location', 0)
            except Exception:
                print('Failed to turn off pointer location on', device.serial)
        raise e

def main(n_trades=100):
    print('\n### AutoTrader by jonaro00 ###\n')
    try:
        asyncio.run(trade_process(n_trades))
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(int(sys.argv[1]))
    else:
        main()
