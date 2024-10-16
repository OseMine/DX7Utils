import os
import json
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu

# Debug-Funktion zum Ausgeben von Nachrichten
def debug_print(message):
    print(f"[DEBUG] {message}")

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        debug_print(f"Konfiguration geladen: {config}")
        return config['directory'], config['dexed_path']
    except FileNotFoundError:
        debug_print("config.json nicht gefunden.")
        sys.exit(1)
    except KeyError:
        debug_print("Pfad im config.json fehlt.")
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

def detect_instrument_type(data):
    if len(data) == 4096 + 6:  # DX7 MK1 format
        return "DX7 MK1"
    elif len(data) == 4096 + 8:  # DX7 II format
        return "DX7 II"
    elif len(data) == 4096 + 7:  # TX802 format
        return "TX802"
    else:
        return "Unknown"

def extract_patch_names(file_path):
    patch_names = []
    instrument_type = "Unknown"
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            instrument_type = detect_instrument_type(data)
            
            if instrument_type == "DX7 MK1":
                offset = 6
                patch_count = 32
            elif instrument_type in ["DX7 II", "TX802"]:
                offset = 8
                patch_count = 32
            else:
                return [], instrument_type

            for i in range(patch_count):
                start = offset + i * 128
                end = start + 10
                patch_bytes = data[start:end]
                patch_name = ''
                for byte in patch_bytes:
                    if byte == 0:
                        break
                    if 32 <= byte <= 127:
                        patch_name += chr(byte)
                    else:
                        patch_name += f'[{byte}]'
                patch_names.append(patch_name.strip())
        
        debug_print(f"Extrahierte Patch-Namen aus {file_path}: {patch_names}")
    except Exception as e:
        debug_print(f"Fehler beim Lesen der Datei {file_path}: {e}")
    
    return patch_names, instrument_type

def search_patch_names(files, search_term):
    results = []
    for file in files:
        patch_names, instrument_type = extract_patch_names(file)
        matching_patches = [(file, i+1, name, instrument_type) for i, name in enumerate(patch_names) if search_term.lower() in name.lower()]
        results.extend(matching_patches)
    results.sort(key=lambda x: (x[2].lower(), x[0]))  # Sortiere nach Patchname und dann nach Dateipfad
    debug_print(f"Sortierte Suchergebnisse: {results}")
    return results

def open_file_in_explorer(file_path):
    try:
        if sys.platform == 'win32':
            os.startfile(file_path)
        elif sys.platform == 'darwin':
            subprocess.call(['open', file_path])
        else:
            subprocess.call(['xdg-open', file_path])
        debug_print(f"Datei im Explorer geöffnet: {file_path}")
    except Exception as e:
        debug_print(f"Fehler beim Öffnen der Datei {file_path}: {e}")

def open_with_dexed(file_path, dexed_path, patch_number):
    try:
        hex_patch = format(patch_number - 1, '02X')
        subprocess.Popen([dexed_path, file_path, f"-p{hex_patch}"])
        debug_print(f"Datei mit Dexed geöffnet: {file_path}, Patch: {patch_number}")
    except Exception as e:
        debug_print(f"Fehler beim Öffnen der Datei mit Dexed: {e}")

class SysexSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sysex Search Tool")
        self.root.geometry("1200x500")

        self.search_label = tk.Label(root, text="Suchbegriff für Yamaha DX7/TX Patch-Namen:")
        self.search_label.pack(pady=10)

        self.search_entry = tk.Entry(root, width=50)
        self.search_entry.pack(pady=5)

        self.search_button = tk.Button(root, text="Suchen", command=self.start_search)
        self.search_button.pack(pady=10)

        self.result_tree = ttk.Treeview(root, columns=('file', 'patch_nr', 'patch_name', 'instrument'), show='headings')
        self.result_tree.heading('file', text='Datei')
        self.result_tree.heading('patch_nr', text='Patch Nr.')
        self.result_tree.heading('patch_name', text='Patch Name')
        self.result_tree.heading('instrument', text='Instrument')
        self.result_tree.column('file', width=400)
        self.result_tree.column('patch_nr', width=80, anchor='center')
        self.result_tree.column('patch_name', width=400)
        self.result_tree.column('instrument', width=120)
        self.result_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.result_tree.bind("<Double-1>", self.on_file_double_click)
        self.result_tree.bind("<Button-3>", self.on_right_click)

        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Öffnen", command=self.context_open_file)
        self.context_menu.add_command(label="Mit Dexed öffnen", command=self.context_open_with_dexed)

        self.directory, self.dexed_path = load_config()
        debug_print(f"Verzeichnis: {self.directory}, Dexed-Pfad: {self.dexed_path}")

    def start_search(self):
        search_term = self.search_entry.get().strip()
        debug_print(f"Suchbegriff: {search_term}")
        if not search_term:
            messagebox.showwarning("Eingabefehler", "Bitte einen Suchbegriff eingeben.")
            return
        
        for i in self.result_tree.get_children():
            self.result_tree.delete(i)

        sysex_files = find_sysex_files(self.directory)
        if not sysex_files:
            messagebox.showwarning("Fehler", "Keine SysEx-Dateien gefunden.")
            return

        results = search_patch_names(sysex_files, search_term)
        if results:
            for file_path, patch_nr, patch_name, instrument_type in results:
                relative_path = os.path.relpath(file_path, self.directory)
                debug_print(f"Gefundener Patch: {relative_path}, Nr. {patch_nr}: {patch_name}, Instrument: {instrument_type}")
                self.result_tree.insert('', 'end', values=(relative_path, patch_nr, patch_name, instrument_type))
        else:
            debug_print(f"Keine Patches für '{search_term}' gefunden.")
            messagebox.showinfo("Keine Übereinstimmung", f"Keine Patches für '{search_term}' gefunden.")

    def on_file_double_click(self, event):
        item = self.result_tree.selection()[0]
        file_path = self.result_tree.item(item, "values")[0]
        full_path = os.path.join(self.directory, file_path)
        debug_print(f"Doppelklick auf Datei: {full_path}")
        open_file_in_explorer(full_path)

    def on_right_click(self, event):
        item = self.result_tree.identify_row(event.y)
        if item:
            self.result_tree.selection_set(item)
            debug_print(f"Rechtsklick auf Item: {item}")
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def context_open_file(self):
        item = self.result_tree.selection()[0]
        file_path = self.result_tree.item(item, "values")[0]
        full_path = os.path.join(self.directory, file_path)
        debug_print(f"Kontextmenü: Öffne Datei {full_path}")
        open_file_in_explorer(full_path)

    def context_open_with_dexed(self):
        item = self.result_tree.selection()[0]
        values = self.result_tree.item(item, "values")
        file_path = values[0]
        patch_number = int(values[1])
        full_path = os.path.join(self.directory, file_path)
        debug_print(f"Kontextmenü: Öffne mit Dexed {full_path}, Patch: {patch_number}")
        open_with_dexed(full_path, self.dexed_path, patch_number)

if __name__ == "__main__":
    debug_print("Starte Anwendung")
    root = tk.Tk()
    app = SysexSearchApp(root)
    root.mainloop()
    debug_print("Anwendung beendet")
