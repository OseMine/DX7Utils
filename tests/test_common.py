import pytest
import os
import sys
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dx7utils.common import identify_instrument, clear_console_line, find_sysex_files, load_config, load_config_simple


class TestIdentifyInstrument:
    def test_dx7_single(self):
        assert identify_instrument(4104) == "Yamaha DX7"

    def test_dx7ii(self):
        assert identify_instrument(4096) == "Yamaha DX7II or TX802"

    def test_dx7s(self):
        assert identify_instrument(4942) == "Yamaha DX7s"

    def test_tx7(self):
        assert identify_instrument(163) == "Yamaha TX7"

    def test_dx1_or_dx5(self):
        assert identify_instrument(4096 * 2) == "Yamaha DX1 or DX5"

    def test_dx7iifd(self):
        assert identify_instrument(4096 * 2 + 8) == "Yamaha DX7IIFD"

    def test_tx816(self):
        assert identify_instrument(4104 * 8) == "Yamaha TX816"

    def test_unknown(self):
        assert identify_instrument(0) == "Unknown"
        assert identify_instrument(100) == "Unknown"


class TestClearConsoleLine:
    def test_runs_without_error(self):
        clear_console_line()


class TestFindSysexFiles:
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_sysex_files(tmpdir)
            assert result == []

    def test_finds_syx_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'test.syx'), 'w').close()
            open(os.path.join(tmpdir, 'test.txt'), 'w').close()
            result = find_sysex_files(tmpdir)
            assert len(result) == 1
            assert result[0].endswith('test.syx')

    def test_finds_nested_syx_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, 'bank')
            os.makedirs(subdir)
            open(os.path.join(subdir, 'nested.syx'), 'w').close()
            open(os.path.join(tmpdir, 'root.syx'), 'w').close()
            result = find_sysex_files(tmpdir)
            assert len(result) == 2


class TestLoadConfig:
    def test_missing_file_exits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                with pytest.raises(SystemExit):
                    load_config()
            finally:
                os.chdir(orig_dir)

    def test_valid_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                config = {"directory": "/some/path", "dexed_path": "/some/dexed"}
                os.makedirs('data', exist_ok=True)
                with open('data/config.json', 'w') as f:
                    json.dump(config, f)
                directory, dexed_path = load_config()
                assert directory == "/some/path"
                assert dexed_path == "/some/dexed"
            finally:
                os.chdir(orig_dir)

    def test_missing_key_exits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs('data', exist_ok=True)
                config = {"wrong_key": "value"}
                with open('data/config.json', 'w') as f:
                    json.dump(config, f)
                with pytest.raises(SystemExit):
                    load_config()
            finally:
                os.chdir(orig_dir)


class TestLoadConfigSimple:
    def test_valid_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs('data', exist_ok=True)
                config = {"directory": "/some/path", "dexed_path": "/some/dexed"}
                with open('data/config.json', 'w') as f:
                    json.dump(config, f)
                result = load_config_simple()
                assert result == "/some/path"
            finally:
                os.chdir(orig_dir)
