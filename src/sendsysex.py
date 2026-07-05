import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

import mido

from dx7utils.common import debug_print


def load_midi_output_port():
    try:
        with open('data/config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("data/config.json nicht gefunden.")
    except json.JSONDecodeError as e:
        raise ValueError(f"data/config.json ist ungültig: {e}")

    midi_port_prefix = config.get('midi_output_port')
    if not midi_port_prefix:
        raise KeyError("MIDI-Ausgangsport in data/config.json fehlt oder ist leer.")
    debug_print(f"MIDI-Ausgangsport-Präfix aus der Konfiguration: {midi_port_prefix}")

    available_ports = mido.get_output_names()
    debug_print(f"Verfügbare MIDI-Ausgangsports: {available_ports}")

    for port in available_ports:
        if port.startswith(midi_port_prefix):
            debug_print(f"Verwendeter MIDI-Ausgangsport: {port}")
            return port

    raise ValueError(f"Kein MIDI-Ausgangsport gefunden, der mit '{midi_port_prefix}' beginnt.")


def send_sysex(file_path):
    midi_output_port = load_midi_output_port()

    file_path = os.path.normpath(file_path)
    debug_print(f"Versuche, die Datei zu öffnen: {file_path}")

    with mido.open_output(midi_output_port) as port:
        with open(file_path, 'rb') as f:
            sysex_data = f.read()

        if not sysex_data.startswith(b'\xF0') or not sysex_data.endswith(b'\xF7'):
            raise ValueError("Die Datei enthält keine gültigen SysEx-Daten.")

        sysex_msg = mido.Message('sysex', data=sysex_data[1:-1])
        port.send(sysex_msg)

        debug_print(f"SysEx-Daten gesendet: {file_path}")


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
