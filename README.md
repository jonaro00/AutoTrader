# AutoTrader

AutoTrader is a Python script that lets 2 (or more 😳) **Android** phones automate trading in Pokémon GO by sending *taps* to the screen. The communication with the device is done with Android Debug Bridge (adb).

## Requirements

- Two (or more) Android devices
- PC with Python 3.10+ and Android Debug Bridge
- At least one USB cable to connect PC and devices
- [Optional] Wifi on the same network as the PC

## Disclaimer

This is a simple tool to make trading less boring.
The absence of batch trading in the game is the main issue/motivator for this project.

Using the script is not error free.
Keep an eye out on the phones while the script is running.

## License

MIT License

## Setup

Start off by cloning or downloading the files in this repo.

### Setting up Python

Install Python 3.10 or higher ([download page](https://www.python.org/downloads/)).

Move to this directory in your shell and install required packages with `pip install -r requirements.txt` (or set up a virtual environment first; see below).

#### Using a venv (optional)

Setting up a Python virtual environment (venv) before installing the dependencies is recommended on Linux,
but also if you are using Python for many things on your system.

If you use a venv, remember to do the activate step before running the `trade.py` script.

The easiest way to get started:

```powershell
# Windows (cmd)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

```sh
# Linux (bash/zsh)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Refer to the [official documentation](https://docs.python.org/3/library/venv.html) for other options and more details.

### Setting up adb (Android Debug Bridge)

Follow the instructions to download adb: <https://developer.android.com/studio/releases/platform-tools>

Make sure that `adb` can be used from the command line. Simplest way is to add the `platform-tools` folder (unzipped) to `PATH`.

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

Connect the phone's Wifi to the same network that the computer is on.
While connected with USB cable, use `adb tcpip 5555` to enable adb over Wifi on the phone.
After this, the phone can be unplugged.
Check your phone's local IP address in **Settings > About phone > Status**, it probably looks something like *192.168.x.x*.
Then, enter it with the command `adb connect <ipaddress>`.
A prompt should show up on the phone again, press *Allow*.
Check that your device is connected with `adb devices`.
This time, the IP address along with the status 'authenticated' should be in the list.

### Upload configuration for AutoTrader to phone

*NOTE: This only needs to be done once per device used!*

In order to know where to tap on the screen, AutoTrader reads a config file `AutoTraderConfig.yaml` from the phone.
It should contain the coordinates of each button for that phone.
This means that phones with identical screen resolutions can probably use the same config file.
This section covers how to create and upload that file.

Make a copy of the file `ConfigTemplate.yaml` and call it whatever you like.
In this example it will be called `MyPhone.yaml`.
Edit this file and replace the `[X, Y]` with the X and Y coordinates of the respective button.
The coordinates only need to be *on* the button, they don't need to be precise at all.
To find the coordinates, turn on the Pointer location tool (**Settings > Developer options > Pointer location**), enter a trade, and read the coordinates from the `X:` and `Y:` fields at the top while holding your finger on the desired button.
**Round to whole numbers**.

- **TRADE_BTN** is the button labeled *TRADE* on the friend screen.
- **FIRST_PKMN_BTN** is the first (top-left) Pokémon in the Pokémon selection menu.
- **NEXT_BTN** is the button labeled *NEXT* after selecting a Pokémon to trade.
- **CONFIRM_BTN** is the button on the left hand side of the trade screen to confirm the trade.
- **X_BTN** is the button to close the Pokémon screen after the trade is done.

Below is an example of a completed config file for a Samsung Galaxy M21 (1080 x 2340 px):

```yml
TRADE_BTN:      [890, 1625]
FIRST_PKMN_BTN: [195,  625]
NEXT_BTN:       [540, 1860]
CONFIRM_BTN:    [153, 1150]
X_BTN:          [540, 2075]
```

Once the coordinates are in the config file, use `adb push MyPhone.yaml /storage/self/primary/AutoTraderConfig.yaml` to upload it.

## Usage

How to use the script when everything is ready.

### In-game preparation

Create a tag with all the Pokémon to trade.

Start a trade manually and search for the tag.
Complete the trade.
The search query for the tag will now be remembered in the upcoming trades.

### Running the script

Connect 2 phones to adb with the steps above.

Execute the script with

- `python trade.py` (Windows)
- `./trade.py` (Linux/Mac)

The script starts by checking for connected devices, then loads config files, and prompts the user with how many trades to perform, after which the trading begins.

The trading process turns on the *Pointer location* tool, both to visualize the automated taps and to serve as an indicator that the script is running.
To cancel the trading process, press **Ctrl+C**.

When trading has finished or is cancelled, the *Pointer location* tool is turned off.
If this fails, it can be turned off manually in **Settings > Developer options > Pointer location**.

#### Custom delay between taps

Some devices and enviroments might experience more or less lag than what the default values are tailored for.
When in the `Number of trades?` prompt, use the command `delay` to get and `delay <value>` to set the delay modifier.
The value can be any floating point number, such as `3`, `3.5`, `0`, or even `-1` if you are feeling brave.
By default, it only affects the **TRADE_BTN**, **NEXT_BTN**, and **CONFIRM_BTN** timings, since those are the ones that involve waiting for the game server.
