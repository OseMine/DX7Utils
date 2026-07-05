# DX7Utils — Usage Guide

## Quick Start

```bash
# Install dependencies
bin/install.bat          # Windows
bash bin/install.sh      # macOS / Linux

# Launch config tool
python -m src.config

# Run a tool
python -m src.midi
python -m src.PatchSearchApp
```

## Setup: Config Tool (`python -m src.config`)

The Tkinter GUI lets you configure:

| Field | Description |
|---|---|
| **Cartridge Ordner** | Directory containing `.syx` files for patch search |
| **Dexed Pfad** | Path to the Dexed VST executable |
| **MIDI Ausgang** | Output port (e.g. loopMIDI) |
| **MIDI Eingang** | Input port from the DX7 |
| **MIDI Kanal** | Channel (1-16) |

Click **Testen und Speichern** to verify MIDI connectivity and save to `data/config.json`.

## Tools

### MIDI CC Remapper (`python -m src.midi`)

Turns the DX7's single data-entry slider (CC 6) into 32 independent CC controls — one per patch.

1. Select the virtual MIDI output port (e.g. loopMIDI)
2. Select the DX7 MIDI input port
3. When you change patches on the DX7 (Program Change 0-31), CC 6 is mapped to that patch's fader
4. Other incoming CC values are forwarded as-is

Use `python -m src.mididebug` for colored console output during development.

### MIDI Backup (`python -m src.midibackup`)

Logs incoming MIDI CC 6 values per program to `data/fader_values.json`. Useful for saving/restoring slider positions across sessions.

### Patch Search GUI (`python -m src.PatchSearchApp`)

Graphical browser for `.syx` patch banks.

1. Enter a search term (partial match, case-insensitive)
2. Results appear in a table with file, patch number, name, and instrument type
3. Right-click a result to:
   - Open the file in Explorer
   - Launch Dexed with that patch
   - Send the patch to the DX7 via SysEx

Search runs in a background thread so the UI stays responsive.

### Patch Search CLI (`python -m src.patchsearchercmd`)

Terminal equivalent of the GUI search:

```bash
Gib den Suchbegriff für den Yamaha DX7 Patch-Namen ein: brass
```

### Send SysEx (`python -m src.sendsysex <file>`)

Sends a `.syx` file to the configured MIDI output port:

```bash
python -m src.sendsysex "C:\Patches\brass.syx"
```

### Read SysEx (`python -m src.readsysex`)

Dumps all patch names from every `.syx` file in the cartridge directory to the console.

### List MIDI Ports (`python -m src.ports`)

Prints all available MIDI input and output port names.

## Configuration File

Saved to `data/config.json`:

```json
{
  "directory": "C:/Users/.../Cartridges",
  "dexed_path": "C:/Program Files/VstPlugins/Dexed.exe",
  "midi_output_port": "loopMIDI Port",
  "midi_input_port": "DX7",
  "midi_channel": 1
}
```
