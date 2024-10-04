import mido
import time
import json

# 32 Variablen, um die Fader-Werte für jedes Programm zu speichern
fader_values = {f'program_{i}': 0 for i in range(32)}

current_program = None  # Aktuelles aktives Programm (0 bis 31)

def clear_console_line():
    """Löscht die aktuelle Zeile in der Konsole."""
    print("\033[A\033[K", end='')

def display_fader_value(fader_value):
    """Gibt den aktuellen Fader-Wert in einer statischen Zeile aus."""
    clear_console_line()
    print(f"Aktuelles Programm: {current_program} | Fader-Wert (CC {current_program}): {fader_value}", end='\r')

def save_to_json(file_name='fader_values.json'):
    """Speichert die Fader-Werte in einer JSON-Datei."""
    with open(file_name, 'w') as file:
        json.dump(fader_values, file, indent=4)
    print(f"\nDaten wurden in {file_name} gespeichert.")

def send_midi_cc(virtual_output, program, value):
    """Sendet eine Control Change Nachricht über das virtuelle MIDI-Gerät."""
    cc_number = program  # CC-Nummer entspricht dem Programm
    msg = mido.Message('control_change', control=cc_number, value=value)
    virtual_output.send(msg)
    print(f"\nGesendete Control Change: CC {cc_number}, Wert {value}")

def main():
    global current_program

    # Zeige verfügbare MIDI-Ausgangsports an
    print("Verfügbare MIDI-Ausgangsports:")
    output_ports = mido.get_output_names()
    for i, port in enumerate(output_ports):
        print(f"{i}: {port}")

    # Virtuelles MIDI-Gerät auswählen (z. B. loopMIDI)
    port_index = int(input("Wähle den virtuellen MIDI-Ausgangsport (Nummer): "))
    virtual_device_name = output_ports[port_index]

    # Versuche, das virtuelle MIDI-Gerät zu öffnen
    try:
        virtual_output = mido.open_output(virtual_device_name)
    except OSError as e:
        print(f"Fehler beim Öffnen des virtuellen MIDI-Geräts: {e}")
        return

    # Zeige verfügbare MIDI-Eingangsports an
    print("Verfügbare MIDI-Eingangsports:")
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
                        current_value = fader_values[f'program_{current_program}']

                        # Nur senden, wenn der Fader-Wert sich geändert hat
                        if msg.value != current_value:
                            fader_values[f'program_{current_program}'] = msg.value
                            display_fader_value(msg.value)

                            # Sende den geänderten Fader-Wert an das virtuelle MIDI-Gerät
                            send_midi_cc(virtual_output, current_program, msg.value)

                time.sleep(0.01)  # Geringe Pause, um die CPU zu schonen
        except KeyboardInterrupt:
            print("\nProgramm beendet.")
        finally:
            # Speichere die Daten in eine JSON-Datei, wenn das Programm beendet wird
            save_to_json()

if __name__ == "__main__":
    main()
