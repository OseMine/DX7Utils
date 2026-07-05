import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mido
import time
from dx7utils.midi_core import fader_values, current_program, load_from_json, save_to_json, send_midi_cc, display_fader_value
from dx7utils.common import debug_print

load_from_json()

def main():
    global current_program

    print("Verfügbare MIDI-Ausgangsports:")
    output_ports = mido.get_output_names()
    debug_print(f"Verfügbare MIDI-Ausgangsports: {output_ports}")

    for i, port in enumerate(output_ports):
        print(f"{i}: {port}")

    port_index = int(input("Wähle den virtuellen MIDI-Ausgangsport (Nummer): "))
    virtual_device_name = output_ports[port_index]
    debug_print(f"Gewählter virtueller MIDI-Ausgangsport: {virtual_device_name}")

    try:
        virtual_output = mido.open_output(virtual_device_name)
        debug_print(f"Virtuelles MIDI-Gerät erfolgreich geöffnet: {virtual_device_name}")
    except OSError as e:
        print(f"Fehler beim Öffnen des virtuellen MIDI-Geräts: {e}")
        return

    print("Verfügbare MIDI-Eingangsports:")
    midi_ports = mido.get_input_names()
    debug_print(f"Verfügbare MIDI-Eingangsports: {midi_ports}")

    for i, port in enumerate(midi_ports):
        print(f"{i}: {port}")

    port_index = int(input("Wähle den MIDI-Eingangsport (Nummer): "))
    midi_input_name = midi_ports[port_index]
    debug_print(f"Gewählter MIDI-Eingangsport: {midi_input_name}")

    try:
        with mido.open_input(midi_input_name) as inport:
            print("Warte auf MIDI-Nachrichten...")
            debug_print("MIDI-Eingang geöffnet und wartet auf Nachrichten")

            try:
                while True:
                    for msg in inport.iter_pending():
                        debug_print(f"Empfangene MIDI-Nachricht: {msg}")

                        if msg.type in ['pitchwheel', 'note_on']:
                            virtual_output.send(msg)
                            debug_print(f"Gesendete Nachricht: {msg}")

                        if msg.type == 'program_change' and 0 <= msg.program <= 31:
                            current_program = msg.program
                            debug_print(f"Programm gewechselt zu: {current_program}")

                        if msg.type == 'control_change' and msg.control != 6 and current_program is not None:
                            fader_values[f'program_{current_program}']['cc_value'] = msg.value
                            cc_value = fader_values[f'program_{current_program}']['cc_value']
                            debug_print(f"Aktueller CC-Wert für Programm {current_program}: {cc_value}")

                            fader_value = fader_values[f'program_{current_program}']['fader_value']
                            display_fader_value(current_program, fader_value, cc_value)

                            send_midi_cc(virtual_output, current_program, cc_value)

                        if msg.type == 'control_change' and msg.control == 6 and current_program is not None:
                            current_value = fader_values[f'program_{current_program}']['fader_value']
                            debug_print(f"Aktueller Fader-Wert für Programm {current_program}: {current_value}")

                            if msg.value != current_value:
                                fader_values[f'program_{current_program}']['fader_value'] = msg.value
                                display_fader_value(current_program, msg.value, fader_values[f'program_{current_program}']['cc_value'])

                                debug_print(f"Neuer Fader-Wert für Programm {current_program}: {msg.value}")
                                debug_print(f"Fader-Werte aktualisiert: {fader_values}")

                                send_midi_cc(virtual_output, current_program, msg.value)

                    time.sleep(0.01)
            except KeyboardInterrupt:
                print("\nProgramm wurde durch den Benutzer beendet.")
                debug_print("Programm durch KeyboardInterrupt beendet")
    except OSError as e:
        print(f"Fehler beim Öffnen des MIDI-Eingangsports: {e}")
    finally:
        save_to_json()
        try:
            virtual_output.close()
        except Exception:
            pass

if __name__ == "__main__":
    debug_print("Programm startet")
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramm wurde durch den Benutzer beendet.")
    debug_print("Programm wurde beendet")
