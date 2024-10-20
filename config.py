import os
import json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import mido
import time
import sys
import threading
import rtmidi

def debug_print(message):
    print(f"[DEBUG] {message}")

class ConfigApp:
    def __init__(self, master):
        self.master = master
        self.master.title("DX7 Konfiguration")
        self.master.geometry("520x400")

        self.load_default_values()

        self.cartridge_path = tk.StringVar(value=self.config['directory'])
        self.dexed_path = tk.StringVar(value=self.config['dexed_path'])
        self.midi_out_port = tk.StringVar(value=self.config['midi_output_port'])
        self.midi_in_port = tk.StringVar(value=self.config['midi_input_port'])
        self.midi_channel = tk.IntVar(value=self.config['midi_channel'])

        self.create_widgets()
        self.midi_monitor_thread = None
        self.stop_midi_monitor = threading.Event()
        self.midi_in = rtmidi.MidiIn()

    def load_default_values(self):
        default_config = {
            "directory": os.path.expandvars("%appdata%\\DigitalSuburban\\Dexed\\Cartridges") if sys.platform == 'win32' else "",
            "dexed_path": "C:/Program Files/VstPlugins/Dexed.exe" if sys.platform == 'win32' else "",
            "midi_output_port": "",
            "midi_input_port": "",
            "midi_channel": 1
        }

        try:
            with open('config.json', 'r') as f:
                stored_config = json.load(f)
            self.config = {**default_config, **stored_config}
            debug_print(f"Werte aus config.json geladen und mit Standardwerten ergänzt: {self.config}")
        except FileNotFoundError:
            self.config = default_config
            debug_print(f"config.json nicht gefunden, verwende Standardwerte: {self.config}")

    def create_widgets(self):
        ttk.Label(self.master, text="Cartridge Ordner:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.cartridge_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Durchsuchen", command=self.browse_cartridge).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.master, text="Dexed Pfad:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.dexed_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Durchsuchen", command=self.browse_dexed).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(self.master, text="MIDI Ausgang:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.midi_out_combo = ttk.Combobox(self.master, textvariable=self.midi_out_port, width=47)
        self.midi_out_combo['values'] = mido.get_output_names()
        self.midi_out_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.master, text="MIDI Eingang:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.midi_in_combo = ttk.Combobox(self.master, textvariable=self.midi_in_port, width=47)
        self.midi_in_combo['values'] = mido.get_input_names()
        self.midi_in_combo.grid(row=3, column=1, padx=5, pady=5)
        self.midi_in_combo.bind("<<ComboboxSelected>>", self.on_midi_in_change)

        ttk.Label(self.master, text="MIDI Kanal:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(self.master, from_=1, to=16, textvariable=self.midi_channel, width=5).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(self.master, text="Testen und Speichern", command=self.test_and_save).grid(row=5, column=1, pady=20)

    def browse_cartridge(self):
        folder = filedialog.askdirectory()
        if folder:
            self.cartridge_path.set(folder)
            debug_print(f"Cartridge Ordner ausgewählt: {folder}")

    def browse_dexed(self):
        file = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if file:
            self.dexed_path.set(file)
            debug_print(f"Dexed Pfad ausgewählt: {file}")

    def on_midi_in_change(self, event):
        if self.midi_monitor_thread:
            self.stop_midi_monitor.set()
            self.midi_monitor_thread.join()
        self.stop_midi_monitor.clear()
        self.midi_monitor_thread = threading.Thread(target=self.monitor_midi_input)
        self.midi_monitor_thread.start()

    def monitor_midi_input(self):
        try:
            ports = self.midi_in.get_ports()
            if self.midi_in_port.get() in ports:
                port_index = ports.index(self.midi_in_port.get())
                if self.midi_in.is_port_open():
                    self.midi_in.close_port()
                self.midi_in.open_port(port_index)
                debug_print(f"MIDI-Überwachung gestartet für Port: {self.midi_in_port.get()}")
                while not self.stop_midi_monitor.is_set():
                    msg = self.midi_in.get_message()
                    if msg:
                        message, delta_time = msg
                        if message[0] & 0xF0 in [0x80, 0x90]:  # Note On oder Note Off
                            channel = message[0] & 0x0F
                            if channel == self.midi_channel.get() - 1:
                                debug_print(f"MIDI-Eingang: {message}")
                    time.sleep(0.001)
                self.midi_in.close_port()
            else:
                debug_print(f"MIDI-Eingangsport {self.midi_in_port.get()} nicht gefunden")
        except Exception as e:
            debug_print(f"Fehler bei der MIDI-Überwachung: {str(e)}")

    def test_and_save(self):
        debug_print("Starte MIDI-Test")
        debug_print(f"Verfügbare MIDI-Eingangsports: {mido.get_input_names()}")
        debug_print(f"Verfügbare MIDI-Ausgangsports: {mido.get_output_names()}")
        
        try:
            output_port = self.midi_out_port.get()
            input_port = self.midi_in_port.get()
            
            if input_port not in mido.get_input_names():
                raise ValueError(f"Der ausgewählte MIDI-Eingangsport '{input_port}' ist nicht verfügbar.")
            if output_port not in mido.get_output_names():
                raise ValueError(f"Der ausgewählte MIDI-Ausgangsport '{output_port}' ist nicht verfügbar.")
            
            debug_print(f"Versuche, MIDI-Ausgangsport zu öffnen: {output_port}")
            with mido.open_output(output_port) as outport:
                debug_print(f"MIDI-Ausgangsport erfolgreich geöffnet: {output_port}")
                
                debug_print(f"Versuche, MIDI-Eingangsport zu öffnen: {input_port}")
                try:
                    if self.midi_in.is_port_open():
                        self.midi_in.close_port()
                    
                    available_ports = self.midi_in.get_ports()
                    if input_port in available_ports:
                        port_index = available_ports.index(input_port)
                        self.midi_in.open_port(port_index)
                        debug_print(f"MIDI-Eingangsport erfolgreich geöffnet: {input_port}")
                    else:
                        raise ValueError(f"MIDI-Eingangsport '{input_port}' nicht gefunden.")
                    
                    channel = self.midi_channel.get() - 1  # MIDI-Kanäle sind 0-basiert
                    note_on = mido.Message('note_on', note=69, velocity=64, channel=channel)
                    outport.send(note_on)
                    debug_print(f"Gesendet: {note_on}")
                    
                    # Start listening for responses immediately
                    start_time = time.time()
                    while time.time() - start_time < 2:  # 2 Sekunden Timeout
                        msg = self.midi_in.get_message()
                        if msg:
                            message, delta_time = msg
                            debug_print(f"Empfangen: {message}")
                            if message[0] & 0xF0 in [0x90, 0x80]:  # Note On oder Note Off
                                self.save_config()
                                debug_print("MIDI-Verbindung erfolgreich getestet und Konfiguration gespeichert")
                                messagebox.showinfo("Erfolg", "MIDI-Verbindung getestet und Konfiguration gespeichert!")
                                break
                    
                    # Send note off after the test
                    note_off = mido.Message('note_off', note=69, velocity=64, channel=channel)
                    outport.send(note_off)
                    debug_print(f"Gesendet: {note_off}")

                    if time.time() - start_time >= 2:
                        debug_print("Keine Antwort vom MIDI-Gerät erhalten")
                        messagebox.showerror("Fehler", "Keine Antwort vom MIDI-Gerät erhalten.")
                    
                    self.midi_in.close_port()
                except rtmidi.RtMidiError as e:
                    debug_print(f"Fehler beim Öffnen des MIDI-Eingangsports: {str(e)}")
                    messagebox.showerror("MIDI-Fehler", f"Fehler beim Öffnen des MIDI-Eingangsports: {str(e)}")
        except ValueError as e:
            debug_print(f"Fehler bei der MIDI-Port-Auswahl: {str(e)}")
            messagebox.showerror("MIDI-Fehler", str(e))
        except OSError as e:
            debug_print(f"MIDI-Port-Fehler: {str(e)}")
            messagebox.showerror("MIDI-Fehler", f"Fehler beim Öffnen des MIDI-Ports: {str(e)}")
        except Exception as e:
            debug_print(f"Allgemeiner Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Unerwarteter Fehler beim MIDI-Test: {str(e)}")

    def save_config(self):
        config = {
            "directory": self.cartridge_path.get(),
            "dexed_path": self.dexed_path.get(),
            "midi_output_port": self.midi_out_port.get(),
            "midi_input_port": self.midi_in_port.get(),
            "midi_channel": self.midi_channel.get()
        }
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        debug_print(f"Konfiguration gespeichert: {config}")

def main():
    debug_print("Starte Konfigurationsanwendung")
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()
    if app.midi_monitor_thread:
        app.stop_midi_monitor.set()
        app.midi_monitor_thread.join()
    if app.midi_in.is_port_open():
        app.midi_in.close_port()
    debug_print("Konfigurationsanwendung beendet")

if __name__ == "__main__":
    main()