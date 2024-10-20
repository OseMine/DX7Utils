import mido

# Zeige alle verfügbaren MIDI-Ausgangsports
available_ports = mido.get_output_names()
print("Verfügbare MIDI-Ausgangsports:")
for port in available_ports:
    print(port)
