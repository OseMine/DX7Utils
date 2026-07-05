import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sendsysex import load_midi_output_port


class TestLoadMidiOutputPort:
    def test_missing_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                with pytest.raises(FileNotFoundError):
                    load_midi_output_port()
            finally:
                os.chdir(orig_dir)

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs('data', exist_ok=True)
                with open('data/config.json', 'w') as f:
                    f.write('not json')
                with pytest.raises(ValueError):
                    load_midi_output_port()
            finally:
                os.chdir(orig_dir)

    def test_missing_port_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs('data', exist_ok=True)
                config = {"wrong_key": "value"}
                with open('data/config.json', 'w') as f:
                    json.dump(config, f)
                with pytest.raises(KeyError):
                    load_midi_output_port()
            finally:
                os.chdir(orig_dir)
