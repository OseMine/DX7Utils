# DX7Utils — Analysis & To-Do

## Bugs & Logic Errors (✓ Resolved)

- [x] **CRITICAL: `sendsysex.py` calls `sys.exit(1)` on all errors** — Replaced with proper exception raising. CLI `__main__` handles exceptions with `sys.exit(1)` only there. Also removed hardcoded `backend='mido.backends.rtmidi'`.

- [x] **Double-send loop in `midi.py`/`mididebug.py`** — Added `and msg.control != 6` to the generic CC handler. CC 6 is now handled exclusively by the fader-specific handler, eliminating duplicate sends.

- [x] **`patchsearchercmd.py` wrong name offset** — Rewrote `extract_patch_names()` to use seek-based parsing (skip 6-byte header, 102+16+10 per voice), matching `PatchSearchApp.py` exactly.

- [x] **`fader_values.json` format mismatch** — Standardised on nested `{"fader_value": 0, "cc_value": 0}` format. `load_from_json()` handles both flat and nested formats for backward compatibility.

- [x] **No load-on-startup for fader values** — Added `load_from_json()` to `midi.py`, `mididebug.py`, and `midibackup.py` — loads saved fader values on startup.

- [x] **Treeview selection crash** — Added `get_selected_item()` guard to all selection handlers in `PatchSearchApp.py`.

- [x] **`display_fader_value()` uses unqualified global** — Now takes `current_program` as explicit parameter.

## Design Issues

### Recently Fixed

- [x] **Thread safety in `config.py`** — Monitor thread is stopped before `test_and_save` accesses `self.midi_in`, restarted after. `monitor_midi_input` caches channel in a local int instead of reading Tkinter IntVar from background thread.

- [x] **Hardcoded rtmidi backend** — Removed `backend='mido.backends.rtmidi'` from `sendsysex.py`, uses default backend now.

### Still Open

- [ ] **Zero test coverage** — No unit or integration tests exist. `.gitignore` has pytest-related entries suggesting it was planned.

- [ ] **Massive code duplication** — `identify_instrument()` copied in 2 files, `extract_patch_names()` implemented 3 different ways, `debug_print()` redefined in every file, `load_config()` duplicated, `find_sysex_files()` duplicated. Extract a shared `dx7utils/` module.

- [ ] **No package structure** — All files are standalone scripts at repo root with no `__init__.py`. Cannot `import dx7utils`. Create a proper package.

- [ ] **GUI search blocks main thread** — `PatchSearchApp.start_search()` runs synchronously, freezing the Tkinter UI for large collections. Use threading or `after()`.

- [ ] **`config.py` doesn't validate paths before saving** — cartridge_path and dexed_path could be empty or invalid.

- [ ] **No virtual environment in install scripts** — `install.bat`/`install.sh` do a global pip install without a venv.

- [ ] **CI tests EOL Python 3.8** — 3.8 is end-of-life since October 2024. Should drop 3.8 and add 3.11/3.12.

- [ ] **CI Windows Cython build likely broken** — `main.yml` Windows build references `%PYTHON_HOME%` which isn't set by `actions/setup-python@v5`.

- [ ] **ANSI escape codes may not work on all Windows terminals** — `clear_console_line()` uses `\033[A\033[K` which fails on old cmd.exe.

- [ ] **`requirements.txt` pins exact versions** — Use `>=` for flexibility with security patches.

## New Feature Ideas

- [ ] **MIDI learn / CC mapping UI** — Let users remap which CC number each program sends, instead of hardcoding CC# = program#
- [ ] **Bulk SysEx librarian** — Save/restore complete DX7 voice banks from the GUI
- [ ] **Patch preview via Dexed** — Auto-launch Dexed with the selected patch for auditioning
- [ ] **Random patch explorer** — Cycle through random patches from the library
- [ ] **Favorites / tagging** — Bookmark patches with user-defined tags for quick recall
- [ ] **MIDI thru with filtering** — Let `midi.py` pass through only selected message types
- [ ] **Auto-detect MIDI port by saved name** — Save port name to config and auto-connect instead of manual selection every time
- [ ] **CLI search with JSON output** — `patchsearchercmd.py` could pipe results as JSON
- [ ] **Cross-platform config paths** — Use platform-agnostic path resolution for cartridge directories
- [ ] **Configuration export/import** — Share DX7 config setups between machines
- [ ] **Start minimised to tray** — `midi.py` could run as a system tray icon instead of a console window
- [ ] **MIDI clock / transport sync** — Use incoming MIDI clock to trigger patch changes in sync
