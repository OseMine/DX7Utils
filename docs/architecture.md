# DX7Utils — Architecture

## Directory Layout

```
DX7Utils/
├── bin/                # Installer scripts
│   ├── install.bat     # Windows setup
│   └── install.sh      # macOS/Linux setup
├── data/               # Runtime config & state (gitignored)
│   ├── config.json     # MIDI ports, cartridge paths, etc.
│   └── fader_values.json  # Saved fader/CC values per program
├── docs/               # Documentation
├── dx7utils/           # Shared library package
│   ├── __init__.py     # Re-exports, colorama init on Windows
│   ├── common.py       # debug_print, clear_console_line, load_config,
│   │                   # find_sysex_files, identify_instrument
│   ├── sysex.py        # extract_patch_names, format_name
│   └── midi_core.py    # fader_values, current_program, load/save JSON,
│                       # send_midi_cc, display_fader_value
├── src/                # Entry-point scripts (runnable)
│   ├── config.py       # Tkinter GUI for configuring MIDI ports & paths
│   ├── midi.py         # MIDI CC remapper (quiet output)
│   ├── mididebug.py    # MIDI CC remapper (colored debug output)
│   ├── midibackup.py   # Logs incoming MIDI to JSON
│   ├── PatchSearchApp.py  # Tkinter GUI for browsing/searching patches
│   ├── patchsearchercmd.py  # CLI version of patch search
│   ├── sendsysex.py    # Sends .syx files to a MIDI port
│   ├── readsysex.py    # Dumps patch names from .syx files to console
│   └── ports.py        # Lists available MIDI ports
├── tests/              # Pytest test suite (25+ tests)
├── .github/workflows/  # CI: build, test, release
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Package Dependency Graph

```
src/config.py  ──────┐
src/midi.py          │
src/mididebug.py     ├── dx7utils.common
src/midibackup.py    │       debug_print, clear_console_line,
src/sendsysex.py     │       load_config, find_sysex_files,
src/readsysex.py ────┘       identify_instrument
                              │
src/PatchSearchApp.py ── dx7utils.sysex
src/patchsearchercmd.py      extract_patch_names, format_name
src/readsysex.py             │
                              │
src/midi.py ──────────── dx7utils.midi_core
src/mididebug.py              fader_values, current_program,
src/midibackup.py             load_from_json, save_to_json,
                              send_midi_cc, display_fader_value
```

All `src/*.py` files prefix their `sys.path` with the project root so `from dx7utils.*` imports work regardless of working directory.

## Data Flow

```
Yamaha DX7
    │
    ├─ MIDI Out ──► loopMIDI ──► src/midi.py ──► VST / DAW
    │                              │
    │                              └─ saves fader_values.json
    │
    ├─ .syx files ──► src/PatchSearchApp.py ──► Dexed / DX7
    │                  src/patchsearchercmd.py
    │                  src/readsysex.py
    │
    └─ config.json ◄── src/config.py (GUI)
```

## Key Design Decisions

- **Package over scripts**: Shared logic lives in `dx7utils/` to eliminate 5-way code duplication that existed originally.
- **Runtime config in `data/`**: JSON files contain user-specific paths and MIDI state and are gitignored.
- **Colorama on Windows**: `dx7utils/__init__.py` auto-calls `colorama.just_fix_windows_console()` for ANSI support on Windows terminals.
- **Thread-safe GUI search**: `PatchSearchApp` runs SysEx parsing in a daemon thread, dispatches results to the main thread via `root.after()`.
