import os
import sys
import json


def debug_print(message):
    print(f"[DEBUG] {message}")


def clear_console_line():
    if os.name == 'nt':
        print(" " * 120, end='\r')
    else:
        print("\033[A\033[K", end='')


def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        debug_print(f"Konfiguration geladen: {config}")
        return config['directory'], config['dexed_path']
    except FileNotFoundError:
        print("config.json nicht gefunden.")
        sys.exit(1)
    except KeyError:
        print("Pfad im config.json fehlt.")
        sys.exit(1)


def load_config_simple():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config['directory']
    except FileNotFoundError:
        print("config.json nicht gefunden.")
        sys.exit(1)
    except KeyError:
        print("Pfad im config.json fehlt.")
        sys.exit(1)


def find_sysex_files(directory):
    sysex_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.syx'):
                full_path = os.path.join(root, file)
                sysex_files.append(full_path)
    debug_print(f"Gefundene SysEx-Dateien: {len(sysex_files)}")
    for file in sysex_files:
        debug_print(f"  {file}")
    return sysex_files


def identify_instrument(file_size):
    if file_size == 4104:
        return "Yamaha DX7"
    elif file_size == 4096:
        return "Yamaha DX7II or TX802"
    elif file_size == 4942:
        return "Yamaha DX7s"
    elif file_size == 163:
        return "Yamaha TX7"
    elif file_size == 4096 * 2:
        return "Yamaha DX1 or DX5"
    elif file_size == 4096 * 2 + 8:
        return "Yamaha DX7IIFD"
    elif file_size == 4104 * 8:
        return "Yamaha TX816"
    else:
        return "Unknown"
