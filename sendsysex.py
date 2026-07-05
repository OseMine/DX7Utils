import mido
import json
import sys
import os

# Debug-Funktion zum Ausgeben von Nachrichten
def debug_print(message):
    print(f"[DEBUG] {message}")

# Lade den MIDI-Ausgangsport-Präfix aus der config.json und wähle den richtigen Ausgang
def load_midi_output_port():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("config.json nicht gefunden.")
    except json.JSONDecodeError as e:
        raise ValueError(f"config.json ist ungültig: {e}")

    midi_port_prefix = config.get('midi_output_port')
    if not midi_port_prefix:
        raise KeyError("MIDI-Ausgangsport in config.json fehlt oder ist leer.")
    debug_print(f"MIDI-Ausgangsport-Präfix aus der Konfiguration: {midi_port_prefix}")
    
    # Alle verfügbaren MIDI-Ausgänge auflisten
    available_ports = mido.get_output_names()
    debug_print(f"Verfügbare MIDI-Ausgangsports: {available_ports}")

    # Finde den Port, der mit dem Präfix übereinstimmt
    for port in available_ports:
        if port.startswith(midi_port_prefix):
            debug_print(f"Verwendeter MIDI-Ausgangsport: {port}")
            return port
    
    raise ValueError(f"Kein MIDI-Ausgangsport gefunden, der mit '{midi_port_prefix}' beginnt.")

# Funktion zum Senden der SysEx-Datei
def send_sysex(file_path):
    midi_output_port = load_midi_output_port()

    # Korrigiere den Pfad unabhängig vom Betriebssystem
    file_path = os.path.normpath(file_path)
    debug_print(f"Versuche, die Datei zu öffnen: {file_path}")

    with mido.open_output(midi_output_port) as port:
        # Lese den Inhalt der SysEx-Datei
        with open(file_path, 'rb') as f:
            sysex_data = f.read()

        # Prüfen, ob es sich um gültige SysEx-Daten handelt (F0 ... F7)
        if not sysex_data.startswith(b'\xF0') or not sysex_data.endswith(b'\xF7'):
            raise ValueError("Die Datei enthält keine gültigen SysEx-Daten.")

        # Erzeuge eine SysEx-Nachricht und sende sie
        sysex_msg = mido.Message('sysex', data=sysex_data[1:-1])  # Entferne F0 und F7 für die Mido-Nachricht
        port.send(sysex_msg)

        debug_print(f"SysEx-Daten gesendet: {file_path}")

# Test-Code, falls das Skript direkt ausgeführt wird
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python sendsysex.py <sysex_file>")
        sys.exit(1)

    sysex_file = sys.argv[1]
    
    if not os.path.isfile(sysex_file):
        print(f"Datei nicht gefunden: {sysex_file}")
        sys.exit(1)

    try:
        send_sysex(sysex_file)
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)
