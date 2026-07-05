import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dx7utils.sysex import format_name, extract_patch_names


class TestFormatName:
    def test_clean_name(self):
        result = format_name(b'BRASS      ')
        assert result == 'BRASS'

    def test_ignores_non_ascii(self):
        result = format_name(b'\x00BRASS\xff')
        assert result == 'BRASS'

    def test_alphanumeric_only(self):
        result = format_name(b'ABCD-1234!')
        assert result == 'ABCD1234'

    def test_empty(self):
        result = format_name(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        assert result == ''


class TestExtractPatchNames:
    def test_invalid_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'nonexistent.syx')
            names, instrument = extract_patch_names(path)
            assert names == []
            assert instrument == "Unknown"

    def test_small_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test.syx')
            with open(path, 'wb') as f:
                f.write(b'\xF0' + b'\x00' * 100 + b'\xF7')
            names, instrument = extract_patch_names(path)
            assert len(names) == 32
            assert instrument == "Unknown"
