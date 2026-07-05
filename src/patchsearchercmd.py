import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dx7utils.common import find_sysex_files, load_config_simple
from dx7utils.sysex import extract_patch_names


def search_patch_names(files, search_term):
    results = {}
    for file in files:
        patch_names, instrument_type = extract_patch_names(file)
        matching_patches = [name for name in patch_names if search_term.lower() in name.lower()]
        if matching_patches:
            results[file] = matching_patches
    return results


def main():
    directory = load_config_simple()
    sysex_files = find_sysex_files(directory)

    if not sysex_files:
        print("Keine SysEx-Dateien gefunden.")
        return

    search_term = input("Gib den Suchbegriff für den Yamaha DX7 Patch-Namen ein: ")

    results = search_patch_names(sysex_files, search_term)

    if results:
        print(f"Gefundene Patches für '{search_term}':")
        for file, patches in results.items():
            print(f"Datei: {file}")
            for patch in patches:
                print(f"  Patch-Name: {patch}")
    else:
        print(f"Keine Patches gefunden, die '{search_term}' entsprechen.")

if __name__ == "__main__":
    main()
