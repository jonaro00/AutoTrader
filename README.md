# AutoTrader

AutoTrader is a Python script that lets 2 (or more 😳) Android phones automate trading in Pokémon GO by sending *taps* to the screen. The communication with the device is done with Android Debug Bridge (adb).

## Requirements

## Disclaimer

## Setup

### Setting up Python

Install Python 3.8 or higher.

Install required packages with `pip install -r requirements.txt`.

### Setting up adb (Android Debug Bridge)

TODO

### Connecting a phone

#### 1. Enable Developer options

Go to **Settings > About phone > Software Information** and tap *Build Number* until developer mode is turned on.

#### 2. Enable USB debugging

Go to **Settings > Developer options** and enable *USB debugging*.

#### 3. Connect adb with phone

Connect the phone to the computer with a USB cable.
Press *Allow* on the prompt that shows up (the adb server must be running for this, see above).
Check that your device is connected with `adb devices`: the serial number along with the status 'device' should be in the list.

#### 4. [Optional] Configure wireless adb

Optionally, you can let adb communicate over Wifi instead of the USB cable.
**This requires that the computer and phone is connected to the same local network**.
If using USB cables is fine, continue to the next section.

While connected with cable, use `adb tcpip 5555` to enable adb over Wifi on the phone.
After this, the phone can be unplugged.
Check your phone's local IP address in **Settings > About phone > Status**, it likely looks something like *192.168.x.x*.
Then, enter it with the command `adb connect <ipaddress>`.
A prompt should show up on the phone again, press *Allow*.
Check that your device is connected with `adb devices`.
This time, the IP address along with the status 'authenticated' should be in the list.

### Upload configuration for AutoTrader to phone

In order to know where to tap on the screen, AutoTrader reads a config file `AutoTraderConfig.json` from your phone.
This section covers how to create and upload that file.

Make a copy of the file `ConfigTemplate.json` and call it whatever you like.
In this example it will be called `MyPhone.json`.
Edit this file and replace the `[X, Y]` with the X and Y coordinates of the respective button.
The coordinates only need to be *on* the button, they don't need to be precise at all.
To find the coordinates, turn on the Pointer location tool (**Settings > Developer options > Pointer location**), enter a trade, and read the coordinates from the `X:` and `Y:` fields at the top while holding your finger on the desired button.
**Round to whole numbers**.

- **TRADE_BTN** is the button labeled *TRADE* on the friend screen.
- **FIRST_PKMN_BTN** is the first (top-left) Pokémon in the Pokémon selection menu.
- **NEXT_BTN** is the button labeled *NEXT* after selecting a Pokémon to trade.
- **CONFIRM_BTN** is the button on the left hand side of the trade screen to confirm the trade.
- **X_BTN** is the button to close the Pokémon screen after the trade is done.

Once the coordinates are in the config file, use `adb push MyPhone.json /storage/self/primary/AutoTraderConfig.json` to upload it.

## Usage

### In-game preparation

Create a tag with all the Pokémon to trade.

Start a trade manually and search for the tag.
Complete the trade.
The search query for the tag will now be remembered in the upcoming trades.

### Using the script

Connect 2 phones to adb with the steps above.

Execute the script with

- `python trade.py` (Windows)
- `./trade.py` (Linux/Mac)

The script starts by checking for connected devices, then loads config files, and prompts the user with how many trades to perform, after which the trading begins.

The trading process turns on the *Pointer location* tool, both to visualize the automated taps and to serve as an indicator that the script is running.
To cancel the trading process, press Ctrl+C.

When a trading batch is finished or cancelled, the *Pointer location* tool is turned off.
If this fails, it can be turned off manually in **Settings > Developer options > Pointer location**.
