import mido
import time
import json

# Farben für Debug-Ausgaben
def debug_message(message):
    """Gibt eine Debug-Nachricht in Grün aus."""
    print(f"\033[92mdebug: {message}\033[0m")  # Grün

def error_message(message):
    """Gibt eine Fehlernachricht in Rot aus."""
    print(f"\033[91merror: {message}\033[0m")  # Rot

# 32 Variablen, um die Fader-Werte und CC-Werte für jedes Programm zu speichern
fader_values = {f'program_{i}': {'fader_value': 0, 'cc_value': 0} for i in range(32)}
debug_message(f"Initiale Fader-Werte: {fader_values}")

current_program = None  # Aktuelles aktives Programm (0 bis 31)
debug_message(f"Aktuelles Programm (Startwert): {current_program}")

def clear_console_line():
    """Löscht die aktuelle Zeile in der Konsole."""
    print("\033[A\033[K", end='')

def display_fader_value(fader_value, cc_value):
    """Gibt den aktuellen Fader-Wert und CC-Wert in einer statischen Zeile aus."""
    clear_console_line()
    print(f"Aktuelles Programm: {current_program} | Fader-Wert (CC {current_program}): {fader_value}, CC Wert: {cc_value}", end='\r')

def save_to_json(file_name='fader_values.json'):
    """Speichert die Fader-Werte in einer JSON-Datei."""
    debug_message("Speichere Fader-Werte in JSON-Datei")
    try:
        with open(file_name, 'w') as file:
            json.dump(fader_values, file, indent=4)
        debug_message(f"Daten wurden in {file_name} gespeichert.")
    except Exception as e:
        error_message(f"Fehler beim Speichern der Fader-Werte: {e}")

def send_midi_cc(virtual_output, program, value):
    """Sendet eine Control Change Nachricht über das virtuelle MIDI-Gerät."""
    cc_number = program  # CC-Nummer entspricht dem aktuell gewählten Programm (Patch)
    msg = mido.Message('control_change', control=cc_number, value=value)
    try:
        virtual_output.send(msg)
        debug_message(f"Gesendete Control Change: CC {cc_number}, Wert {value}")
    except Exception as e:
        error_message(f"Fehler beim Senden der MIDI-Nachricht: {e}")

def main():
    global current_program

    # Zeige verfügbare MIDI-Ausgangsports an
    print("Verfügbare MIDI-Ausgangsports:")
    output_ports = mido.get_output_names()
    debug_message(f"Verfügbare MIDI-Ausgangsports: {output_ports}")
    
    for i, port in enumerate(output_ports):
        print(f"{i}: {port}")

    # Virtuelles MIDI-Gerät auswählen (z. B. loopMIDI)
    port_index = int(input("Wähle den virtuellen MIDI-Ausgangsport (Nummer): "))
    virtual_device_name = output_ports[port_index]
    debug_message(f"Gewählter virtueller MIDI-Ausgangsport: {virtual_device_name}")

    # Versuche, das virtuelle MIDI-Gerät zu öffnen
    try:
        virtual_output = mido.open_output(virtual_device_name)
        debug_message(f"Virtuelles MIDI-Gerät erfolgreich geöffnet: {virtual_device_name}")
    except OSError as e:
        error_message(f"Fehler beim Öffnen des virtuellen MIDI-Geräts: {e}")
        return

    # Zeige verfügbare MIDI-Eingangsports an
    print("Verfügbare MIDI-Eingangsports:")
    midi_ports = mido.get_input_names()
    debug_message(f"Verfügbare MIDI-Eingangsports: {midi_ports}")
    
    for i, port in enumerate(midi_ports):
        print(f"{i}: {port}")

    # MIDI-Port wählen, der den Yamaha DX7 empfängt
    port_index = int(input("Wähle den MIDI-Eingangsport (Nummer): "))
    midi_input_name = midi_ports[port_index]
    debug_message(f"Gewählter MIDI-Eingangsport: {midi_input_name}")

    try:
        with mido.open_input(midi_input_name) as inport:
            print("Warte auf MIDI-Nachrichten...")
            debug_message("MIDI-Eingang geöffnet und wartet auf Nachrichten")

            try:
                while True:
                    for msg in inport.iter_pending(): 
                        # Zeige jede empfangene MIDI-Nachricht an
                        debug_message(f"Empfangene MIDI-Nachricht: {msg}")

                        # Direktes Senden spezifischer MIDI-Nachrichtentypen
                        if msg.type in ['pitchwheel', 'control_change', 'note_on']:
                            virtual_output.send(msg)
                            debug_message(f"Gesendete Nachricht: {msg}")

                        # Wenn eine Program Change-Nachricht empfangen wird
                        if msg.type == 'program_change' and 0 <= msg.program <= 31:
                            # Setze das aktuelle Programm, wodurch der gewählte CC bestimmt wird
                            current_program = msg.program
                            debug_message(f"Programm gewechselt zu: {current_program}")

                        # Wenn eine Control Change-Nachricht empfangen wird
                        if msg.type == 'control_change' and current_program is not None:
                            # Aktualisiere den CC-Wert für das aktuelle Programm
                            fader_values[f'program_{current_program}']['cc_value'] = msg.value
                            cc_value = fader_values[f'program_{current_program}']['cc_value']
                            debug_message(f"Aktueller CC-Wert für Programm {current_program}: {cc_value}")

                            # Aktualisiere den Fader-Wert, wenn CC-Wert sich ändert
                            fader_value = fader_values[f'program_{current_program}']['fader_value']
                            display_fader_value(fader_value, cc_value)

                            # Sende den geänderten CC-Wert mit der entsprechenden CC-Nummer
                            send_midi_cc(virtual_output, current_program, cc_value)

                        # Wenn eine spezielle Control Change-Nachricht für Fader (CC 6) empfangen wird
                        if msg.type == 'control_change' and msg.control == 6 and current_program is not None:
                            # Lese den aktuellen Fader-Wert des gewählten Programms
                            current_value = fader_values[f'program_{current_program}']['fader_value']
                            debug_message(f"Aktueller Fader-Wert für Programm {current_program}: {current_value}")

                            # Nur senden, wenn der Fader-Wert sich geändert hat
                            if msg.value != current_value:
                                # Speichere den neuen Fader-Wert
                                fader_values[f'program_{current_program}']['fader_value'] = msg.value
                                display_fader_value(msg.value, fader_values[f'program_{current_program}']['cc_value'])

                                debug_message(f"Neuer Fader-Wert für Programm {current_program}: {msg.value}")
                                debug_message(f"Fader-Werte aktualisiert: {fader_values}")

                                # Sende den geänderten Fader-Wert mit der entsprechenden CC-Nummer
                                send_midi_cc(virtual_output, current_program, msg.value)

                    time.sleep(0.01)  # Geringe Pause, um die CPU zu schonen
            except KeyboardInterrupt:
                print("\nProgramm wurde durch den Benutzer beendet.")
                debug_message("Programm durch KeyboardInterrupt beendet")
    except OSError as e:
        error_message(f"Fehler beim Öffnen des MIDI-Eingangsports: {e}")
    finally:
        # Speichere die Daten in eine JSON-Datei, wenn das Programm beendet wird
        save_to_json()

if __name__ == "__main__":
    debug_message("Programm startet")
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramm wurde durch den Benutzer beendet.")
    debug_message("Programm wurde beendet")
