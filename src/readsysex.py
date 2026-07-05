import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from dx7utils.common import find_sysex_files
from dx7utils.sysex import extract_patch_names


def main():
    with open('data/config.json', 'r') as config_file:
        config = json.load(config_file)

    directory = config['directory']
    sysex_files = find_sysex_files(directory)

    for syx_file_path in sysex_files:
        try:
            patch_names, instrument = extract_patch_names(syx_file_path)
            print(f"Datei: {syx_file_path}")
            print(f"Instrument: {instrument}")
            print("Patch-Namen:")
            for i, name in enumerate(patch_names, 1):
                print(f"  - Voice {i:3d}: {name}")
            print()
        except Exception as e:
            print(f"Fehler beim Verarbeiten von {syx_file_path}: {str(e)}")

if __name__ == "__main__":
    main()
