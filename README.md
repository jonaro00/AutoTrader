# AutoTrader

AutoTrader is a Python script that lets 2 (or more 😳) Android phones automate trading in Pokémon GO by sending *taps* to the screen.

## Setup

### Setting up Python

Install Python 3.6 or higher.

Install required packages with `pip install -r requirements.txt`.

### Setting up adb (Android Debug Bridge)

TODO

### Connecting a phone

#### 1. Enable Developer options

Go to **Settings > About phone > Software Information** and tap *Build Number* until developer mode is turned on.

#### 2. Enable USB debugging

Go to **Settings > Developer options**, find and enable *USB debugging*.

#### 3. Connect adb with phone

Connect the phone to the computer with a USB cable.

Press *Allow* on the prompt that shows up.

Check that your device is connected with `adb devices`.

#### 4. [Optional] Configure wireless adb

*Optionally, you can let adb communicate over Wifi instead of the USB cable. This requires that the computer and phone is connected to the same local network.*

While connected with cable, use `adb tcpip 5555` to enable adb over Wifi on the phone. After this, the phone can be unplugged.

Check your phone's IP address in **Settings > About phone > Status > IP address**. It usually starts with `192.168`.

Use `adb connect <ipaddress>` and press *Allow* on the prompt.

Check that your device is connected with `adb devices`.

### Upload configuration for AutoTrader to phone

*In order to know where to tap on the screen, AutoTrader reads a config file `AutoTraderConfig.json` from your phone. This section covers how to create and upload that file.*

Make a copy of the file `ConfigTemplate.json` and call it whatever you like. In this example it will be called `MyPhone.json`.

Edit your config file and replace the `[X, Y]` with the X and Y coordinates of the respective button. The coordinates only need to be *on* the button, they don't need to be precise at all. To find the coordinates, turn on the Pointer location tool (**Settings > Developer options > Pointer location**), enter a trade, and read the coordinates from the `X:` and `Y:` fields while holding your finger on the desired button. **Round to whole numbers**.

- **TRADE_BTN** is the button labeled *TRADE* on the friend screen.
- **FIRST_PKMN_BTN** is the first (top-left) Pokémon in the Pokémon selection menu.
- **NEXT_BTN** is the button labeled *NEXT* after selecting a Pokémon to trade.
- **CONFIRM_BTN** is the button on the left hand side of the trade screen to confirm the trade.
- **X_BTN** is the button to close the Pokémon screen after the trade is done.

Once the coordinates are in the config file, use `adb push MyPhone.json /storage/self/primary/AutoTraderConfig.json` to upload it.

## Usage

### In-game preparation

Create a tag with all the Pokémon to trade.

Start a trade manually and search for the tag. Complete the trade. The search will now be remembered in the upcoming trades.

### Using the script

Connect 2 phones to adb with the steps above.

Execute the script with

- `python trade.py <n_trades>` (Windows)
- `python3 trade.py <n_trades>` (Linux)

where *n_trades* is the number of trades to perform (default is 100).

The script checks for devices and loads config files. Then, after a confirmation from the user, it turns on the Pointer location tool (to visualize the automated taps), and executes *n_trades* trading sequences.

To cancel the trading process, press Ctrl+C.

When finished or cancelled, the Pointer location tool is turned off. If this fails, it can be turned off in Developer options.
