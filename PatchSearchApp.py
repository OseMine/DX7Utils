import os
import json
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu
import sendsysex as send

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
        return "Unknown"

def extract_patch_names(file_path):
    patch_names = []
    instrument_type = "Unknown"
    try:
        file_size = os.path.getsize(file_path)
        instrument_type = identify_instrument(file_size)
        
        with open(file_path, 'rb') as f:
            f.read(6)  # Header überspringen
            
            if instrument_type in ["Yamaha DX1 or DX5", "Yamaha DX7IIFD"]:
                num_voices = 64
            elif instrument_type == "Yamaha TX816":
                num_voices = 256
            else:
                num_voices = 32
            
            for voice_number in range(num_voices):
                f.read(6 * 17)  # Operator-Daten überspringen
                f.read(16)  # Globale Parameter überspringen
                name_data = f.read(10)
                patch_name = ''.join(c for c in name_data.decode('ascii', 'ignore') if c.isalnum())
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
    results.sort(key=lambda x: (x[2].lower(), x[0]))
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
        self.context_menu.add_command(label="An DX7 senden", command=self.send_to_dx7)
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
    
    def send_to_dx7(self):
        item = self.result_tree.selection()[0]
        file_path = self.result_tree.item(item, "values")[0]
        full_path = os.path.join(self.directory, file_path)
        self.send_sysex(full_path)
    def send_sysex(self, file_path):
        try:
            send.send_sysex(file_path)
            print(f'Gesendet: {file_path}')
        except Exception as e:
            print(f'Fehler beim Senden: {e}')
            messagebox.showerror("Fehler", f"Fehler beim Senden der Datei: {e}")
    


if __name__ == "__main__":
    debug_print("Starte Anwendung")
    root = tk.Tk()
    app = SysexSearchApp(root)
    root.mainloop()
    debug_print("Anwendung beendet")
