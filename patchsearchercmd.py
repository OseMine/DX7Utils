import os
import json
import sys

# Funktion zum Laden des Verzeichnisses aus der config.json
def load_config():
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

# Funktion, um rekursiv alle .syx-Dateien in einem Verzeichnis zu finden
def find_sysex_files(directory):
    sysex_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.syx'):
                sysex_files.append(os.path.join(root, file))
    return sysex_files

# Funktion zum Extrahieren der Patch-Namen aus einer SysEx-Datei
def extract_patch_names(file_path):
    patch_names = []
    try:
        with open(file_path, 'rb') as f:
            f.read(6)  # SysEx-Header überspringen (F0 43 00 09 20 00)
            for i in range(32):  # 32 Patches pro Bank
                f.read(6 * 17)  # Operator-Daten überspringen (6 Operatoren à 17 Bytes)
                f.read(16)      # Globale Parameter überspringen
                name_data = f.read(10)  # 10-Byte Patch-Name
                patch_name = name_data.decode('ascii', errors='ignore').strip()
                patch_names.append(patch_name)
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
    return patch_names

# Funktion zum Durchsuchen der extrahierten Patch-Namen nach einem Suchbegriff
def search_patch_names(files, search_term):
    results = {}
    for file in files:
        patch_names = extract_patch_names(file)
        matching_patches = [name for name in patch_names if search_term.lower() in name.lower()]
        if matching_patches:
            results[file] = matching_patches
    return results

# Hauptprogramm
def main():
    directory = load_config()
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
