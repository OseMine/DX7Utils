import mido
import time
import json

# 32 Variablen, um die Fader-Werte und CC-Werte für jedes Programm zu speichern
fader_values = {f'program_{i}': {'fader_value': 0, 'cc_value': 0} for i in range(32)}

current_program = None  # Aktuelles aktives Programm (0 bis 31)

def load_from_json(file_name='fader_values.json'):
    """Lädt die Fader-Werte aus einer JSON-Datei, falls vorhanden."""
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
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Fehler beim Laden der Fader-Werte: {e}")

load_from_json()

def clear_console_line():
    """Löscht die aktuelle Zeile in der Konsole."""
    print("\033[A\033[K", end='')

def display_fader_value(program, fader_value):
    """Gibt den aktuellen Fader-Wert in einer statischen Zeile aus."""
    clear_console_line()
    print(f"Aktuelles Programm: {program} | Fader-Wert (CC 6): {fader_value}", end='\r')

def save_to_json(file_name='fader_values.json'):
    """Speichert die Fader-Werte in einer JSON-Datei."""
    try:
        with open(file_name, 'w') as file:
            json.dump(fader_values, file, indent=4)
        print(f"\nDaten wurden in {file_name} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Fader-Werte: {e}")

def main():
    global current_program

    # Zeige verfügbare MIDI-Eingangsports an
    print("Verfügbare MIDI-Ports:")
    midi_ports = mido.get_input_names()
    for i, port in enumerate(midi_ports):
        print(f"{i}: {port}")

    # MIDI-Port wählen
    port_index = int(input("Wähle den MIDI-Eingangsport (Nummer): "))
    with mido.open_input(midi_ports[port_index]) as inport:
        print("Warte auf MIDI-Nachrichten...")

        try:
            while True:
                for msg in inport.iter_pending():
                    # Zeige jede empfangene MIDI-Nachricht an
                    print(f"\nEmpfangene MIDI-Nachricht: {msg}")

                    # Wenn eine Program Change-Nachricht empfangen wird
                    if msg.type == 'program_change' and 0 <= msg.program <= 31:
                        current_program = msg.program
                        print(f"\nProgramm gewechselt zu: {current_program}")

                    # Wenn eine Control Change-Nachricht für Fader (CC 6) empfangen wird
                    if msg.type == 'control_change' and msg.control == 6 and current_program is not None:
                        fader_values[f'program_{current_program}']['fader_value'] = msg.value
                        display_fader_value(current_program, msg.value)

                time.sleep(0.01)  # Geringe Pause, um die CPU zu schonen
        except KeyboardInterrupt:
            print("\nProgramm beendet.")
        finally:
            # Speichere die Daten in eine JSON-Datei, wenn das Programm beendet wird
            save_to_json()

if __name__ == "__main__":
    main()
