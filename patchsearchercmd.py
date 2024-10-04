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
            data = f.read()
            
            # Die Yamaha DX7 SysEx-Daten beginnen in der Regel mit F0 (Sysex Start) und enden mit F7 (Sysex End)
            # Die Patch-Namen bestehen normalerweise aus 10 ASCII-Zeichen und sind im DX7 SysEx gespeichert
            # DX7 SysEx-Dump: Patch-Namen befinden sich an einer bestimmten Position, z.B. bei Bytes 118 bis 127 für jeden Patch
            
            # Annehmen, dass Patch-Namen an festen Positionen in der Datei sind
            for i in range(32):  # 32 Patches pro Bank
                start = 118 + i * 128  # Dies ist eine grobe Annahme für die Position der Patch-Namen
                end = start + 10
                patch_name = data[start:end].decode('ascii', errors='ignore').strip()
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
