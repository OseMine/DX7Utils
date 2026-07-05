# DX7Utils — Development Guide

## Setup

```bash
git clone https://github.com/OseMine/DX7Utils.git
cd DX7Utils
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v
```

All tests are in `tests/` and use `pytest`. The test suite currently has 25 tests covering:

- `identify_instrument()` — all known file sizes
- `format_name()` — ASCII filtering, non-ASCII stripping
- `extract_patch_names()` — empty and short files
- `clear_console_line()` — error-free execution
- `find_sysex_files()` — empty dir, flat dir, nested dir
- `load_config()` / `load_config_simple()` — missing file, valid config, missing key
- `load_midi_output_port()` — missing config, invalid JSON, missing port key

## Adding Tests

1. Create a new file `tests/test_<module>.py`
2. Import the functions you want to test (the `sys.path` fixture in existing tests adds the project root)
3. Use `tempfile.TemporaryDirectory` and `os.chdir` to test file-dependent functions in isolation

Example:

```python
import pytest
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dx7utils.common import identify_instrument

class TestIdentifyInstrument:
    def test_dx7_single(self):
        assert identify_instrument(4104) == "Yamaha DX7"
```

## Code Style

- **No comments in code** unless the logic is non-obvious
- Import from `dx7utils.*` rather than duplicating functions
- Run `pytest` before committing
- Use `python -m src.<name>` for invocation, never `python src/<name>.py` directly (though both work)

## Project Conventions

| Convention | Rule |
|---|---|
| **Shared code** | Goes in `dx7utils/`, never duplicated |
| **Scripts** | Entry points in `src/`, thin wrapper + import from `dx7utils` |
| **Runtime data** | `data/` directory, gitignored |
| **Tests** | `tests/`, pytest-style |
| **Imports** | `from dx7utils.<module> import <func>` with sys.path boilerplate |

## CI Pipeline

Defined in `.github/workflows/`:

- **main.yml**: Compiles all Python scripts to standalone executables via Cython on Linux, macOS, and Windows
- **ci.yml**: Runs on PRs and pushes (Python 3.9-3.12)
- **release.yml**: Creates GitHub releases with pre-built binaries

## Debugging

- `python -m src.mididebug` enables colored console output for the MIDI remapper
- `debug_print()` from `dx7utils.common` is used throughout instead of bare `print()`
