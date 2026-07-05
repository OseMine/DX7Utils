import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import mido

from dx7utils.common import debug_print, find_sysex_files
from dx7utils.midi_core import (
    fader_values,
    load_from_json,
    save_to_json,
    send_midi_cc,
)
from dx7utils.sysex import extract_patch_names


# ──────────────────────────────────────────────
#  MIDI Ports anzeigen
# ──────────────────────────────────────────────
class PortsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Ports")
        self.root.geometry("500x400")

        ttk.Label(root, text="MIDI Ausgänge:", font=("Segoe UI", 10, "bold")).pack(
            padx=10, pady=(10, 0), anchor=tk.W
        )
        self.out_list = tk.Listbox(root, height=8)
        self.out_list.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(root, text="MIDI Eingänge:", font=("Segoe UI", 10, "bold")).pack(
            padx=10, pady=(10, 0), anchor=tk.W
        )
        self.in_list = tk.Listbox(root, height=8)
        self.in_list.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(root, text="Aktualisieren", command=self.refresh).pack(pady=10)
        self.refresh()

    def refresh(self):
        self.out_list.delete(0, tk.END)
        for p in mido.get_output_names():
            self.out_list.insert(tk.END, p)
        self.in_list.delete(0, tk.END)
        for p in mido.get_input_names():
            self.in_list.insert(tk.END, p)


# ──────────────────────────────────────────────
#  SysEx senden
# ──────────────────────────────────────────────
class SendSysexUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SysEx senden")
        self.root.geometry("600x200")

        ttk.Label(root, text="SysEx-Datei:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        file_frame = ttk.Frame(root)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Durchsuchen", command=self.browse).pack(side=tk.LEFT, padx=5)

        ttk.Label(root, text="MIDI Ausgang:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(root, textvariable=self.port_var, state="readonly")
        self.port_combo.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(root, text="Senden", command=self.send).pack(pady=10)
        self.status_label = ttk.Label(root, text="")
        self.status_label.pack()
        self.refresh_ports()

    def browse(self):
        f = filedialog.askopenfilename(filetypes=[("SysEx", "*.syx"), ("Alle", "*.*")])
        if f:
            self.file_path.set(f)

    def refresh_ports(self):
        ports = mido.get_output_names()
        self.port_combo["values"] = ports
        if ports:
            self.port_var.set(ports[0])

    def send(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("Fehler", "Datei nicht gefunden")
            return
        port_name = self.port_var.get()
        if not port_name:
            messagebox.showerror("Fehler", "Kein MIDI-Port ausgewählt")
            return
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if not data.startswith(b"\xF0") or not data.endswith(b"\xF7"):
                raise ValueError("Keine gültigen SysEx-Daten")
            with mido.open_output(port_name) as port:
                msg = mido.Message("sysex", data=data[1:-1])
                port.send(msg)
            messagebox.showinfo("Erfolg", f"Gesendet: {os.path.basename(file_path)}")
            self.status_label.config(text="Gesendet")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            self.status_label.config(text=f"Fehler: {e}")


# ──────────────────────────────────────────────
#  SysEx lesen
# ──────────────────────────────────────────────
class ReadSysexUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SysEx lesen")
        self.root.geometry("900x500")

        top = ttk.Frame(root)
        top.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(top, text="Aktualisieren", command=self.refresh).pack(side=tk.LEFT)
        self.info_label = ttk.Label(top, text="")
        self.info_label.pack(side=tk.LEFT, padx=10)

        columns = ("file", "patch_nr", "patch_name", "instrument")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("file", text="Datei")
        self.tree.heading("patch_nr", text="Nr.")
        self.tree.heading("patch_name", text="Patch-Name")
        self.tree.heading("instrument", text="Instrument")
        self.tree.column("file", width=400)
        self.tree.column("patch_nr", width=50, anchor="center")
        self.tree.column("patch_name", width=300)
        self.tree.column("instrument", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            with open("data/config.json") as f:
                config = json.load(f)
        except FileNotFoundError:
            self.info_label.config(text="data/config.json nicht gefunden")
            return
        directory = config.get("directory", "")
        if not directory:
            self.info_label.config(text="Kein Verzeichnis konfiguriert")
            return
        files = find_sysex_files(directory)
        count = 0
        for file_path in files:
            try:
                patch_names, instrument = extract_patch_names(file_path)
                rel = os.path.relpath(file_path, directory)
                for i, name in enumerate(patch_names, 1):
                    self.tree.insert("", "end", values=(rel, i, name, instrument))
                count += 1
            except Exception:
                pass
        self.info_label.config(text=f"{count} Dateien, {len(self.tree.get_children())} Patches")


# ──────────────────────────────────────────────
#  MIDI Fader / Debug (generic MIDI relay)
# ──────────────────────────────────────────────
class _MidiRelayUI:
    def __init__(self, root, debug_mode=False):
        self.debug_mode = debug_mode
        self.root = root
        title = "MIDI Debug" if debug_mode else "MIDI Fader"
        self.root.title(title)
        self.root.geometry("700x500")

        ttk.Label(root, text="MIDI Eingang:").grid(row=0, column=0, padx=10, pady=(10, 0), sticky=tk.W)
        ttk.Label(root, text="MIDI Ausgang:").grid(row=1, column=0, padx=10, sticky=tk.W)
        self.in_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.in_combo = ttk.Combobox(root, textvariable=self.in_var, state="readonly", width=50)
        self.out_combo = ttk.Combobox(root, textvariable=self.out_var, state="readonly", width=50)
        self.in_combo.grid(row=0, column=1, padx=10, pady=(10, 0), sticky=tk.W)
        self.out_combo.grid(row=1, column=1, padx=10, sticky=tk.W)

        self.start_btn = ttk.Button(root, text="Starten", command=self.toggle)
        self.start_btn.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        self.status_label = ttk.Label(root, text="", foreground="gray")
        self.status_label.grid(row=3, column=0, columnspan=2, padx=10, sticky=tk.W)

        self.log_text = tk.Text(root, height=16, state=tk.DISABLED)
        self.log_text.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 10), sticky=tk.NSEW)
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

        self.running = False
        self.thread = None
        self.current_program = None
        self.refresh_ports()

    def refresh_ports(self):
        self.in_combo["values"] = mido.get_input_names()
        self.out_combo["values"] = mido.get_output_names()

    def log(self, msg):
        self.root.after(0, lambda: self._append_log(msg))

    def _append_log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def toggle(self):
        if self.running:
            self.running = False
            self.start_btn.config(text="Starten")
            self.status_label.config(text="")
        else:
            in_port = self.in_var.get()
            out_port = self.out_var.get()
            if not in_port or not out_port:
                return
            self.running = True
            self.start_btn.config(text="Stoppen")
            self.status_label.config(text=f"{'Debug' if self.debug_mode else 'Verbunden'}: {in_port} -> {out_port}")
            self.thread = threading.Thread(
                target=self.run_relay, args=(in_port, out_port), daemon=True
            )
            self.thread.start()

    def run_relay(self, in_name, out_name):
        try:
            with mido.open_input(in_name) as inport, mido.open_output(out_name) as outport:
                while self.running:
                    for msg in inport.iter_pending():
                        prefix = "[Rx] " if self.debug_mode else ""
                        self.log(f"{prefix}{msg}")
                        if msg.type in ("pitchwheel", "note_on"):
                            outport.send(msg)
                            if self.debug_mode:
                                self.log(f"[Tx] {msg}")
                        if msg.type == "program_change" and 0 <= msg.program <= 31:
                            self.current_program = msg.program
                            self.log(f"{'[PRG]' if self.debug_mode else ''} Programm {self.current_program}")
                        if msg.type == "control_change" and self.current_program is not None:
                            key = f"program_{self.current_program}"
                            if msg.control != 6:
                                fader_values[key]["cc_value"] = msg.value
                                send_midi_cc(outport, self.current_program, msg.value)
                            elif msg.value != fader_values[key]["fader_value"]:
                                fader_values[key]["fader_value"] = msg.value
                                send_midi_cc(outport, self.current_program, msg.value)
                                self.log(f"Fader {self.current_program} -> {msg.value}")
                    time.sleep(0.01)
        except Exception as e:
            self.log(f"Fehler: {e}")
        finally:
            save_to_json()


# ──────────────────────────────────────────────
#  MIDI Backup
# ──────────────────────────────────────────────
class MidiBackupUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Backup")
        self.root.geometry("600x400")

        ttk.Label(root, text="MIDI Eingang:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(root, textvariable=self.port_var, state="readonly")
        self.port_combo.pack(fill=tk.X, padx=10, pady=5)

        self.start_btn = ttk.Button(root, text="Starten", command=self.toggle)
        self.start_btn.pack(pady=5)
        self.status_label = ttk.Label(root, text="", foreground="gray")
        self.status_label.pack()

        self.log_text = tk.Text(root, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.running = False
        self.thread = None
        self.current_program = None
        self.refresh_ports()

    def refresh_ports(self):
        ports = mido.get_input_names()
        self.port_combo["values"] = ports
        if ports:
            self.port_var.set(ports[0])

    def log(self, msg):
        self.root.after(0, lambda: self._append_log(msg))

    def _append_log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def toggle(self):
        if self.running:
            self.running = False
            self.start_btn.config(text="Starten")
            self.status_label.config(text="")
        else:
            port_name = self.port_var.get()
            if not port_name:
                return
            self.running = True
            self.start_btn.config(text="Stoppen")
            self.status_label.config(text=f"Überwache: {port_name}")
            self.thread = threading.Thread(target=self.monitor, args=(port_name,), daemon=True)
            self.thread.start()

    def monitor(self, port_name):
        try:
            with mido.open_input(port_name) as inport:
                while self.running:
                    for msg in inport.iter_pending():
                        self.log(f"Empfangen: {msg}")
                        if msg.type == "program_change" and 0 <= msg.program <= 31:
                            self.current_program = msg.program
                            self.log(f"Programm: {self.current_program}")
                        if msg.type == "control_change" and msg.control == 6 and self.current_program is not None:
                            key = f"program_{self.current_program}"
                            fader_values[key]["fader_value"] = msg.value
                            self.log(f"Fader {self.current_program}: value={msg.value}")
                    time.sleep(0.01)
        except Exception as e:
            self.log(f"Fehler: {e}")
        finally:
            save_to_json()
            self.root.after(0, lambda: self.status_label.config(text="Beendet"))


# ──────────────────────────────────────────────
#  Dispatcher
# ──────────────────────────────────────────────
UI_CLASSES = {
    "ports": PortsUI,
    "sendsysex": SendSysexUI,
    "readsysex": ReadSysexUI,
    "midi": lambda r: _MidiRelayUI(r, debug_mode=False),
    "mididebug": lambda r: _MidiRelayUI(r, debug_mode=True),
    "midibackup": MidiBackupUI,
}


def launch_ui(tool_name, root):
    load_from_json()
    cls = UI_CLASSES.get(tool_name)
    if cls:
        return cls(root)


def main(tool_name):
    root = tk.Tk()
    launch_ui(tool_name, root)
    root.mainloop()
