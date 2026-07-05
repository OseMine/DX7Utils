import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import mido

from dx7utils.common import debug_print


class ConfigApp:
    def __init__(self, master):
        self.master = master
        self.master.title("DX7 Konfiguration")
        self.master.geometry("620x420")

        self.load_default_values()

        self.cartridge_path = tk.StringVar(value=self.config['directory'])
        self.dexed_path = tk.StringVar(value=self.config['dexed_path'])
        self.midi_out_port = tk.StringVar(value=self.config['midi_output_port'])
        self.midi_in_port = tk.StringVar(value=self.config['midi_input_port'])
        self.midi_channel = tk.IntVar(value=self.config['midi_channel'])

        self.midi_monitor_thread = None
        self.stop_midi_monitor = threading.Event()
        self.midi_input = None
        self.midi_status = tk.StringVar(value="")

        self.create_widgets()
        self.refresh_ports()

    def load_default_values(self):
        default_dir = (
            os.path.expandvars(
                "%appdata%\\DigitalSuburban\\Dexed\\Cartridges"
            )
            if sys.platform == 'win32'
            else ""
        )
        default_dexed = (
            "C:/Program Files/VstPlugins/Dexed.exe"
            if sys.platform == 'win32'
            else ""
        )
        default_config = {
            "directory": default_dir,
            "dexed_path": default_dexed,
            "midi_output_port": "",
            "midi_input_port": "",
            "midi_channel": 1,
        }

        try:
            with open('data/config.json', 'r') as f:
                stored_config = json.load(f)
            self.config = {**default_config, **stored_config}
            debug_print(
                f"Werte aus data/config.json geladen: {self.config}"
            )
        except FileNotFoundError:
            self.config = default_config
            debug_print(
                "data/config.json nicht gefunden, "
                "verwende Standardwerte"
            )

    def create_widgets(self):
        row = 0
        ttk.Label(self.master, text="Cartridge Ordner:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            self.master, textvariable=self.cartridge_path, width=60
        ).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(
            self.master, text="Durchsuchen",
            command=self.browse_cartridge
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(self.master, text="Dexed Pfad:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            self.master, textvariable=self.dexed_path, width=60
        ).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(
            self.master, text="Durchsuchen",
            command=self.browse_dexed
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(self.master, text="MIDI Ausgang:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        self.midi_out_combo = ttk.Combobox(
            self.master, textvariable=self.midi_out_port, width=57
        )
        self.midi_out_combo.grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.master, text="MIDI Eingang:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        self.midi_in_combo = ttk.Combobox(
            self.master, textvariable=self.midi_in_port, width=57
        )
        self.midi_in_combo.grid(row=row, column=1, padx=5, pady=5)
        self.midi_in_combo.bind(
            "<<ComboboxSelected>>", self.on_midi_in_change
        )

        row += 1
        ttk.Label(self.master, text="MIDI Kanal:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        spin = ttk.Spinbox(
            self.master, from_=1, to=16,
            textvariable=self.midi_channel, width=5
        )
        spin.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        btn_frame = ttk.Frame(self.master)
        btn_frame.grid(row=row, column=1, pady=15, sticky="w")
        ttk.Button(
            btn_frame, text="Ports aktualisieren",
            command=self.refresh_ports
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Testen und Speichern",
            command=self.test_and_save
        ).pack(side=tk.LEFT, padx=5)

        row += 1
        ttk.Label(self.master, textvariable=self.midi_status).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )

    def refresh_ports(self):
        out_ports = mido.get_output_names()
        in_ports = mido.get_input_names()
        self.midi_out_combo['values'] = out_ports
        self.midi_in_combo['values'] = in_ports
        debug_print(f"Verfügbare MIDI-Ausgänge: {out_ports}")
        debug_print(f"Verfügbare MIDI-Eingänge: {in_ports}")

    def browse_cartridge(self):
        folder = filedialog.askdirectory()
        if folder:
            self.cartridge_path.set(folder)
            debug_print(f"Cartridge Ordner ausgewählt: {folder}")

    def browse_dexed(self):
        file = filedialog.askopenfilename(
            filetypes=[("Executable", "*.exe")]
        )
        if file:
            self.dexed_path.set(file)
            debug_print(f"Dexed Pfad ausgewählt: {file}")

    def start_midi_monitor(self):
        if self.midi_monitor_thread:
            self.stop_midi_monitor.set()
            self.midi_monitor_thread.join()
        self.stop_midi_monitor.clear()
        self.midi_monitor_thread = threading.Thread(
            target=self.monitor_midi_input, daemon=True
        )
        self.midi_monitor_thread.start()

    def stop_midi_monitor_if_running(self):
        if self.midi_monitor_thread:
            self.stop_midi_monitor.set()
            self.midi_monitor_thread.join()
            self.midi_monitor_thread = None

    def on_midi_in_change(self, event):
        self.start_midi_monitor()

    def monitor_midi_input(self):
        port_name = self.midi_in_port.get()
        if not port_name or port_name not in mido.get_input_names():
            self.master.after(
                0, lambda: self.midi_status.set(
                    f"Eingang '{port_name}' nicht verfügbar"
                )
            )
            return
        try:
            with mido.open_input(port_name) as inport:
                self.master.after(
                    0, lambda: self.midi_status.set(
                        f"Überwache: {port_name}"
                    )
                )
                debug_print(
                    f"MIDI-Überwachung gestartet: {port_name}"
                )
                channel = self.midi_channel.get() - 1
                while not self.stop_midi_monitor.is_set():
                    for msg in inport.iter_pending():
                        if msg.type in ['note_on', 'note_off']:
                            if msg.channel == channel:
                                debug_print(
                                    f"MIDI-Eingang: {msg}"
                                )
                    time.sleep(0.01)
        except OSError as e:
            err_msg = str(e)
            debug_print(f"MIDI-Überwachungsfehler: {err_msg}")
            self.master.after(
                0, lambda m=err_msg: self.midi_status.set(
                    f"Fehler: {m}"
                )
            )

    def test_and_save(self):
        debug_print("Starte MIDI-Test")
        self.stop_midi_monitor_if_running()
        self.midi_status.set("Teste MIDI...")

        output_port = self.midi_out_port.get()
        input_port = self.midi_in_port.get()

        if input_port not in mido.get_input_names():
            msg = (
                f"Eingangsport '{input_port}' "
                "nicht verfügbar"
            )
            debug_print(msg)
            messagebox.showerror("MIDI-Fehler", msg)
            self.midi_status.set("Fehler: Eingang nicht verfügbar")
            return
        if output_port not in mido.get_output_names():
            msg = (
                f"Ausgangsport '{output_port}' "
                "nicht verfügbar"
            )
            debug_print(msg)
            messagebox.showerror("MIDI-Fehler", msg)
            self.midi_status.set("Fehler: Ausgang nicht verfügbar")
            return

        try:
            with (
                mido.open_output(output_port) as outport,
                mido.open_input(input_port) as inport,
            ):
                debug_print(
                    f"Ports geöffnet: out={output_port}, "
                    f"in={input_port}"
                )
                channel = self.midi_channel.get() - 1

                note_on = mido.Message(
                    'note_on', note=69, velocity=64,
                    channel=channel
                )
                outport.send(note_on)
                debug_print(f"Gesendet: {note_on}")

                start = time.time()
                response = False
                while time.time() - start < 2:
                    for msg in inport.iter_pending():
                        if msg.type in ['note_on', 'note_off']:
                            debug_print(f"Empfangen: {msg}")
                            self.save_config()
                            response = True
                            messagebox.showinfo(
                                "Erfolg",
                                "MIDI-Verbindung getestet "
                                "und gespeichert!"
                            )
                            self.midi_status.set(
                                f"Verbunden: {input_port}"
                            )
                            break
                    if response:
                        break
                    time.sleep(0.01)

                note_off = mido.Message(
                    'note_off', note=69, velocity=64,
                    channel=channel
                )
                outport.send(note_off)
                debug_print(f"Gesendet: {note_off}")

                if not response:
                    debug_print("Keine MIDI-Antwort erhalten")
                    messagebox.showerror(
                        "Fehler",
                        "Keine Antwort vom MIDI-Gerät."
                    )
                    self.midi_status.set("Keine Antwort")

        except OSError as e:
            debug_print(f"MIDI-Port-Fehler: {str(e)}")
            messagebox.showerror(
                "MIDI-Fehler",
                f"Port-Fehler: {str(e)}"
            )
            self.midi_status.set(f"Fehler: {str(e)}")
        except Exception as e:
            debug_print(f"Allgemeiner Fehler: {str(e)}")
            messagebox.showerror(
                "Fehler",
                f"Unerwarteter Fehler: {str(e)}"
            )
            self.midi_status.set("Fehler aufgetreten")
        finally:
            if self.midi_in_port.get() in mido.get_input_names():
                self.start_midi_monitor()
    def validate_paths(self):
        errors = []
        cartridge = self.cartridge_path.get().strip()
        dexed = self.dexed_path.get().strip()

        if not cartridge:
            errors.append("Cartridge Ordner darf nicht leer sein.")
        elif not os.path.isdir(cartridge):
            errors.append(
                f"Cartridge Ordner existiert nicht: {cartridge}"
            )

        if not dexed:
            errors.append("Dexed Pfad darf nicht leer sein.")
        elif not os.path.isfile(dexed):
            errors.append(
                f"Dexed Datei existiert nicht: {dexed}"
            )

        return errors

    def save_config(self):
        path_errors = self.validate_paths()
        if path_errors:
            debug_print(f"Pfad-Fehler: {path_errors}")
            messagebox.showerror(
                "Pfad-Fehler", "\n".join(path_errors)
            )
            return

        config = {
            "directory": self.cartridge_path.get().strip(),
            "dexed_path": self.dexed_path.get().strip(),
            "midi_output_port": self.midi_out_port.get(),
            "midi_input_port": self.midi_in_port.get(),
            "midi_channel": self.midi_channel.get(),
        }
        os.makedirs('data', exist_ok=True)
        with open('data/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        debug_print(f"Konfiguration gespeichert: {config}")


def main():
    debug_print("Starte Konfigurationsanwendung")
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()
    app.stop_midi_monitor.set()
    if app.midi_monitor_thread:
        app.midi_monitor_thread.join()
    debug_print("Konfigurationsanwendung beendet")


if __name__ == "__main__":
    main()
