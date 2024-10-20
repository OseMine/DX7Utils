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
        midi_port_prefix = config['midi_output_port']
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
    
    except FileNotFoundError:
        debug_print("config.json nicht gefunden.")
        sys.exit(1)
    except KeyError:
        debug_print("MIDI-Ausgangsport in config.json fehlt.")
        sys.exit(1)
    except ValueError as e:
        debug_print(str(e))
        sys.exit(1)

# Funktion zum Senden der SysEx-Datei
def send_sysex(file_path):
    midi_output_port = load_midi_output_port()

    try:
        # Korrigiere den Pfad unabhängig vom Betriebssystem
        file_path = os.path.normpath(file_path)
        debug_print(f"Versuche, die Datei zu öffnen: {file_path}")

        # Spezifizieren, dass rtmidi verwendet wird (robuster auf Windows)
        with mido.open_output(midi_output_port, backend='mido.backends.rtmidi') as port:
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

    except IOError as e:
        debug_print(f"Fehler beim Öffnen der Datei {file_path}: {e}")
        sys.exit(1)
    except ValueError as e:
        debug_print(f"Fehlerhafte SysEx-Daten in {file_path}: {e}")
        sys.exit(1)
    except mido.backends.rtmidi.OutputError as e:
        debug_print(f"MIDI-Ausgangsfehler: {e}")
        sys.exit(1)
    except Exception as e:
        debug_print(f"Allgemeiner Fehler: {e}")
        sys.exit(1)

# Test-Code, falls das Skript direkt ausgeführt wird
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python sendsysex.py <sysex_file>")
        sys.exit(1)

    sysex_file = sys.argv[1]
    
    if not os.path.isfile(sysex_file):
        print(f"Datei nicht gefunden: {sysex_file}")
        sys.exit(1)

    send_sysex(sysex_file)
