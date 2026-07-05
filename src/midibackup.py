import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

import mido

from dx7utils.midi_core import (
    display_fader_value,
    fader_values,
    load_from_json,
    save_to_json,
)

load_from_json()

def main():
    global current_program

    print("Verfügbare MIDI-Ports:")
    midi_ports = mido.get_input_names()
    for i, port in enumerate(midi_ports):
        print(f"{i}: {port}")

    port_index = int(input("Wähle den MIDI-Eingangsport (Nummer): "))
    with mido.open_input(midi_ports[port_index]) as inport:
        print("Warte auf MIDI-Nachrichten...")

        try:
            while True:
                for msg in inport.iter_pending():
                    print(f"\nEmpfangene MIDI-Nachricht: {msg}")

                    if msg.type == 'program_change' and 0 <= msg.program <= 31:
                        current_program = msg.program
                        print(f"\nProgramm gewechselt zu: {current_program}")

                    if msg.type == 'control_change' and msg.control == 6 and current_program is not None:
                        fader_values[f'program_{current_program}']['fader_value'] = msg.value
                        cc = fader_values[f'program_{current_program}']['cc_value']
                        display_fader_value(current_program, msg.value, cc)

                time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nProgramm beendet.")
        finally:
            save_to_json()

if __name__ == "__main__":
    main()
