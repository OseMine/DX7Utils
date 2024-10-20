import os
import json
import struct

def format_name(name):
    return ''.join(c for c in name.decode('ascii', 'ignore') if c.isalnum())

def identify_instrument(file_size):
    if file_size == 4104:  # 4096 + 8 bytes header/footer
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
        return "Unbekanntes Instrument"

def extract_patch_names(filename):
    with open(filename, 'rb') as file:
        file_size = os.path.getsize(filename)
        instrument = identify_instrument(file_size)
        
        file.read(6)  # Header überspringen
        patch_names = []
        
        # Anzahl der Voices basierend auf dem Instrument bestimmen
        if instrument in ["Yamaha DX1 or DX5", "Yamaha DX7IIFD"]:
            num_voices = 64
        elif instrument == "Yamaha TX816":
            num_voices = 256
        else:
            num_voices = 32
        
        for voice_number in range(num_voices):
            file.read(6 * 17)  # Operator-Daten überspringen
            file.read(16)  # Globale Parameter überspringen
            name_data = file.read(10)
            patch_names.append((voice_number + 1, format_name(name_data)))
    return instrument, patch_names

def main():
    # Config-Datei lesen
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    directory = config['directory']

    # Verzeichnis durchlaufen und .syx-Dateien verarbeiten
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.syx'):
                syx_file_path = os.path.join(root, file)
                try:
                    instrument, patch_names = extract_patch_names(syx_file_path)
                    print(f"Datei: {syx_file_path}")
                    print(f"Instrument: {instrument}")
                    print("Patch-Namen:")
                    for voice_number, name in patch_names:
                        print(f"  - Voice {voice_number:3d}: {name}")
                    print()  # Leerzeile für bessere Lesbarkeit
                except Exception as e:
                    print(f"Fehler beim Verarbeiten von {syx_file_path}: {str(e)}")

if __name__ == "__main__":
    main()
