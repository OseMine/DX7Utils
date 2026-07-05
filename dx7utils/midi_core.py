import os
import json
import mido
from dx7utils.common import debug_print, clear_console_line

fader_values = {f'program_{i}': {'fader_value': 0, 'cc_value': 0} for i in range(32)}

current_program = None


def load_from_json(file_name='data/fader_values.json'):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
        for key, value in data.items():
            if key in fader_values:
                if isinstance(value, dict):
                    fader_values[key]['fader_value'] = value.get('fader_value', 0)
                    fader_values[key]['cc_value'] = value.get('cc_value', 0)
                else:
                    fader_values[key]['fader_value'] = value
        debug_print(f"Fader-Werte aus {file_name} geladen.")
    except FileNotFoundError:
        debug_print(f"{file_name} nicht gefunden, verwende Standardwerte.")
    except Exception as e:
        print(f"Fehler beim Laden der Fader-Werte: {e}")


def save_to_json(file_name='data/fader_values.json'):
    debug_print("Speichere Fader-Werte in JSON-Datei")
    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w') as file:
            json.dump(fader_values, file, indent=4)
        print(f"\nDaten wurden in {file_name} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Fader-Werte: {e}")


def send_midi_cc(virtual_output, program, value):
    cc_number = program
    msg = mido.Message('control_change', control=cc_number, value=value)
    try:
        virtual_output.send(msg)
        debug_print(f"Gesendete Control Change: CC {cc_number}, Wert {value}")
    except Exception as e:
        print(f"Fehler beim Senden der MIDI-Nachricht: {e}")


def display_fader_value(program, fader_value, cc_value):
    clear_console_line()
    print(f"Aktuelles Programm: {program} | Fader-Wert (CC {program}): {fader_value}, CC Wert: {cc_value}", end='\r')
