# DX7Utils — Analysis & To-Do

## Bugs & Logic Errors (✓ Resolved)

- [x] **CRITICAL: `sendsysex.py` calls `sys.exit(1)` on all errors** — Replaced with proper exception raising. CLI `__main__` handles exceptions with `sys.exit(1)` only there. Also removed hardcoded `backend='mido.backends.rtmidi'`.

- [x] **Double-send loop in `midi.py`/`mididebug.py`** — Added `and msg.control != 6` to the generic CC handler. CC 6 is now handled exclusively by the fader-specific handler, eliminating duplicate sends.

- [x] **`patchsearchercmd.py` wrong name offset** — Rewrote `extract_patch_names()` to use seek-based parsing (skip 6-byte header, 102+16+10 per voice), matching `PatchSearchApp.py` exactly.

- [x] **`fader_values.json` format mismatch** — Standardised on nested `{"fader_value": 0, "cc_value": 0}` format. `load_from_json()` handles both flat and nested formats for backward compatibility.

- [x] **No load-on-startup for fader values** — Added `load_from_json()` to `midi.py`, `mididebug.py`, and `midibackup.py` — loads saved fader values on startup.

- [x] **Treeview selection crash** — Added `get_selected_item()` guard to all selection handlers in `PatchSearchApp.py`.

- [x] **`display_fader_value()` uses unqualified global** — Now takes `current_program` as explicit parameter.

## Design Issues (✓ All Resolved)

### Fixed in First Pass

- [x] **Thread safety in `config.py`** — Monitor thread is stopped before `test_and_save` accesses `self.midi_in`, restarted after. `monitor_midi_input` caches channel in a local int instead of reading Tkinter IntVar from background thread.

- [x] **Hardcoded rtmidi backend** — Removed `backend='mido.backends.rtmidi'` from `sendsysex.py`, uses default backend now.

### Fixed in Second Pass

- [x] **Zero test coverage** — `tests/` directory added with tests for `identify_instrument`, `format_name`, `extract_patch_names`, `clear_console_line`, `find_sysex_files`, `load_config`, `load_midi_output_port`. Run with `pytest` from repo root.

- [x] **Massive code duplication** — Extracted shared functions into `dx7utils/common.py` (`debug_print`, `clear_console_line`, `load_config`, `load_config_simple`, `find_sysex_files`, `identify_instrument`), `dx7utils/sysex.py` (`extract_patch_names`, `format_name`), and `dx7utils/midi_core.py` (`fader_values`, `current_program`, `load_from_json`, `save_to_json`, `send_midi_cc`, `display_fader_value`). All files import from these shared modules.

- [x] **No package structure** — Created `dx7utils/` package with `__init__.py` that re-exports key functions. Package auto-initializes colorama on Windows for ANSI support.

- [x] **GUI search blocks main thread** — `PatchSearchApp.start_search()` now runs `_run_search` in a background thread. The search button is disabled during the search, and results are populated via `root.after()` on the main thread.

- [x] **`config.py` doesn't validate paths before saving** — Added `validate_paths()` method that checks cartridge and dexed paths exist before saving. Errors shown in a messagebox.

- [x] **No virtual environment in install scripts** — `install.bat` and `install.sh` now create and activate a `.venv` before installing dependencies.

- [x] **CI tests EOL Python 3.8** — Already handled: `ci.yml` tests 3.9–3.12, `pylint.yml` was deleted.

- [x] **CI Windows Cython build likely broken** — Already fixed in CI workflow: replaced `%PYTHON_HOME%` with `sys.prefix` for correct include/libs paths.

- [x] **ANSI escape codes may not work on all Windows terminals** — `clear_console_line()` in `dx7utils/common.py` checks `os.name` and uses spaces+carriage return on Windows. `dx7utils/__init__.py` calls `colorama.just_fix_windows_console()` on Windows for ANSI support in other places.

- [x] **`requirements.txt` pins exact versions** — Changed `==` to `>=` for flexibility with security patches.

## New Feature Ideas (Still Open — Not Planned for Current Sprint)

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
