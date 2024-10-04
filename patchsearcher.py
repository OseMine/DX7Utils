import os
import json
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Menu

# Funktion zum Laden des Verzeichnisses und des Dexed-Pfads aus der config.json
def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config['directory'], config['dexed_path']
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
            for i in range(32):  # 32 Patches pro Bank
                start = 118 + i * 128
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

# Funktion zum Öffnen der Datei im Explorer oder Finder
def open_file_in_explorer(file_path):
    try:
        if sys.platform == 'win32':  # Windows
            os.startfile(file_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux/Unix
            subprocess.call(['xdg-open', file_path])
    except Exception as e:
        print(f"Fehler beim Öffnen der Datei {file_path}: {e}")

# Funktion, um Dexed zu starten und die ausgewählte SysEx-Datei zu laden
def open_with_dexed(file_path, dexed_path):
    try:
        subprocess.Popen([dexed_path, file_path])
    except Exception as e:
        print(f"Fehler beim Öffnen der Datei mit Dexed: {e}")

# Haupt-GUI-Klasse
class SysexSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sysex Search Tool")
        self.root.geometry("600x400")

        # Label und Eingabefeld für den Suchbegriff
        self.search_label = tk.Label(root, text="Suchbegriff für Yamaha DX7 Patch-Namen:")
        self.search_label.pack(pady=10)

        self.search_entry = tk.Entry(root, width=50)
        self.search_entry.pack(pady=5)

        # Suchbutton
        self.search_button = tk.Button(root, text="Suchen", command=self.start_search)
        self.search_button.pack(pady=10)

        # Listbox zur Anzeige der Suchergebnisse
        self.result_listbox = Listbox(root, width=80, height=15)
        self.result_listbox.pack(pady=10)
        self.result_listbox.bind("<Double-Button-1>", self.on_file_double_click)
        self.result_listbox.bind("<Button-3>", self.on_right_click)  # Rechtsklick für das Kontextmenü

        # Kontextmenü
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Öffnen", command=self.context_open_file)
        self.context_menu.add_command(label="Mit Dexed öffnen", command=self.context_open_with_dexed)

        # Verzeichnis und Dexed-Pfad aus config.json laden
        self.directory, self.dexed_path = load_config()

    # Funktion zum Starten der Suche
    def start_search(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Eingabefehler", "Bitte einen Suchbegriff eingeben.")
            return
        
        self.result_listbox.delete(0, tk.END)  # Listbox leeren

        sysex_files = find_sysex_files(self.directory)
        if not sysex_files:
            messagebox.showwarning("Fehler", "Keine SysEx-Dateien gefunden.")
            return

        results = search_patch_names(sysex_files, search_term)
        if results:
            for file, patches in results.items():
                # Pfad relativ zum Basisverzeichnis anzeigen
                relative_path = os.path.relpath(file, self.directory)
                self.result_listbox.insert(tk.END, f"{relative_path}")
        else:
            messagebox.showinfo("Keine Übereinstimmung", f"Keine Patches für '{search_term}' gefunden.")

    # Doppelklick-Ereignis in der Listbox
    def on_file_double_click(self, event):
        selection = self.result_listbox.curselection()
        if selection:
            # Den relativen Pfad wieder in den absoluten umwandeln
            relative_path = self.result_listbox.get(selection[0])
            full_path = os.path.join(self.directory, relative_path)
            open_file_in_explorer(full_path)

    # Rechtsklick-Ereignis für Kontextmenü
    def on_right_click(self, event):
        try:
            # Ermittlung der ausgewählten Datei bei Rechtsklick
            self.result_listbox.selection_clear(0, tk.END)
            widget = event.widget
            index = widget.nearest(event.y)
            widget.selection_set(index)
            # Position für das Kontextmenü
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # Kontextmenü-Option: Datei im Explorer öffnen
    def context_open_file(self):
        selection = self.result_listbox.curselection()
        if selection:
            relative_path = self.result_listbox.get(selection[0])
            full_path = os.path.join(self.directory, relative_path)
            open_file_in_explorer(full_path)

    # Kontextmenü-Option: Datei mit Dexed öffnen
    def context_open_with_dexed(self):
        selection = self.result_listbox.curselection()
        if selection:
            relative_path = self.result_listbox.get(selection[0])
            full_path = os.path.join(self.directory, relative_path)
            open_with_dexed(full_path, self.dexed_path)

# Start der Anwendung
if __name__ == "__main__":
    root = tk.Tk()
    app = SysexSearchApp(root)
    root.mainloop()
