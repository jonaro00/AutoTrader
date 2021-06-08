import asyncio
from time import sleep
from ppadb.client_async import ClientAsync


TRADE_BTN = 890, 1625
FIRST_PKMN_BTN = 195, 625
NEXT_BTN = 540, 1860
CONFIRM_BTN = 153, 1150
X_BTN = 540, 2075

async def tap(dev, point):
    x, y = point
    x2, y2 = x+1, y+1
    cmd = f'input swipe {x} {y} {x2} {y2} 100'
    await dev.shell(cmd)

async def trade_sequence(devs):
    await asyncio.gather(*(tap(dev, TRADE_BTN) for dev in devs))
    sleep(4)
    await asyncio.gather(*(tap(dev, FIRST_PKMN_BTN) for dev in devs))
    sleep(2)
    await asyncio.gather(*(tap(dev, NEXT_BTN) for dev in devs))
    sleep(2)
    await asyncio.gather(*(tap(dev, CONFIRM_BTN) for dev in devs))
    sleep(19)
    await asyncio.gather(*(tap(dev, X_BTN) for dev in devs))
    sleep(1)

async def main():
    client = ClientAsync()
    devices = await client.devices()
    if not devices:
        print('No devices found')
        return

    for i in range(1, 101):
        print('Starting sequence', i)
        await trade_sequence(devices)

if __name__ == '__main__':
    asyncio.run(main())
