# DX7Utils

DX7Utils is a set of utilities designed to enhance the experience of using the Yamaha DX7 synthesizer alongside a PC, especially for users who lack a separate master keyboard. This repository includes tools for MIDI debugging and patch searching, making it easier to manage patches and interact with your DX7.

## Features

### 1. Config
`config.py` is the gui based configuration for the whole project. It enables to set a path for the SysEx Cartridges and to Set Midi input/output ports with autotesting of the ports. more functionality will come in the future

### 2.MIDI TOOL
`mididebug.py`/`midi.py` enables the use of the Data Entry slider (MIDI CC 6) in combination with the 32 patch buttons (MIDI Program Change 0-31) as 32 individual MIDI CC inputs. This setup is particularly useful if you don’t have a dedicated master keyboard, allowing you to control various parameters on the DX7.

To use `mididebug.py`/`midi.py`, you'll need a virtual MIDI port (e.g., [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)) that intercepts and forwards MIDI CC data to your software or hardware synth. Once configured, this tool allows you to maximize your DX7’s control capabilities without additional equipment.

### 3. Patch Search App
`PatchSearchApp.py` is a tool for searching DX7 SysEx files for specific patches. With this utility, you can quickly find patches within your collection, streamlining the process of locating sounds and loading them onto your DX7.

### 4. SysEx Sendung Tool
`sendsysex.py` enables the sending of SysEx data

## Requirements
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) or another virtual MIDI port utility
- Python 3.x
- compatible Hardware:
	 - `patchsearcher.py`: Any Yamaha DX/FM synth which uses the same SysEx Format as the DX7
	 - `mididebug.py`/`midi.py`: A Yamaha DX7 MK1 (tested), Yamaha DX7II/S (not tested) or any other Yamaha DX Synth (might need a code adjustment)
    - `sendsysex.py`: Any Synth/mid compatible gear which can recieve SysEx (Testet) or any Midi Data (not testet)

## Usage

### Setup
1. Configure `loopMIDI` or another virtual MIDI port tool.
2. Clone this repository:
   ```bash
   git clone https://github.com/OseMine/DX7Utils.git
   cd DX7Utils
   ```
3. Install the necessary dependencies by running the `install.sh` file (for MacOs an Linux) or the `install.bat` file (for Windows)
4. Maybe disable The Debug Messages in the `patchsearcher.py`, by opening it with any Text editor and chang these lines
  ```python
    def debug_print(message):
    print(f"[DEBUG] {message}")
  ```
to these lines
  ```python
    def debug_print(message):
    #print(f"[DEBUG] {message}")
  ```
5. Run the `config.py` file, by running `python config.py`, to set up your Midi devices and SysEx File Locations
6. Run the utility of your choice.

### Running `mididebug.py`
Use `mididebug.py` to enhance your control setup by executing:

  ```bash
   python mididebug.py
   ```
   (good for developing, because of the Debug Messages),

OR

   ```bash
   python midi.py
   ```
   (without the Debug Messages)

### Running `PatchSearchApp.py`
To search through your SysEx files for specific patches, execute:
   ```bash
   python patchsearcher.py
   ```
### Running `sendsysex.py`
To send SysEx commands to the configured Midi Ports exexute:
   ```bash
   python sendsysex.py <sysex_file>
   ```
## TODOs

### General
- Translate the entire project from German to English.
- Implement multilingual support for broader accessibility.

### `config.py`
- optimizibg ghe midi connecticity
- optimizing the auto calibration/midi port testing

### `sensysex.py`
- optimizibg ghe midi connecticity

### `patchsearcher.py`
- Enhance patch-to-instrument mapping for better organization.
- Integrate `PatchSearchApp.py` more seamlessly with the Dexed emulator/Patch editor.
- Develop an in-app patch browser for easier navigation.
- Improve performance and efficiency.
- Improve sending SysEx files directly to Yamaha DX7, DX7S, DX7II, TX7, and TX802 synthesizers.

### `mididebug.py`
- Optimize performance and reduce latency.
- Improve CC conversion for compatibility with a broader range of software and MIDI CC hardware synthesizers.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit a pull request.

## Contact
For questions or support, please reach out to the project maintainer (@OseMine) by sending me A DM on Instagram ([@the.muzikar](https://www.instagram.com/the.muzikar/) or contacting via [Email](mailto:oskar.wiedrich@gmail.com)).

Enjoy using DX7Utils and happy synthesizing!