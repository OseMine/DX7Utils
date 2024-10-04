import struct
import os

# Funktion zum Lesen der Binärdaten aus der Datei
def read_binary_file(filename):
    with open(filename, 'rb') as file:
        data = file.read()
    return data

# Funktion zum Bearbeiten der Binärdaten (Beispiel: Daten modifizieren)
def modify_binary_data(data, offset, new_value):
    # Wir nehmen an, dass die Daten 4 Bytes groß sind (z.B. ein unsigned int)
    new_data = bytearray(data)  # Binärdaten in ein bytearray konvertieren, damit sie veränderbar sind
    
    # Neuen Wert in binäres Format umwandeln
    packed_value = struct.pack('I', new_value)  # 'I' steht für unsigned int (4 Bytes)
    
    # Die neuen Daten an der gewünschten Stelle einsetzen
    new_data[offset:offset+4] = packed_value  # Offset + 4, weil ein unsigned int 4 Bytes groß ist
    
    return bytes(new_data)

# Funktion zum Speichern der modifizierten Binärdaten
def save_binary_file(filename, data):
    # Stelle sicher, dass du Schreibrechte hast, da die Datei in einem geschützten Verzeichnis liegt
    with open(filename, 'wb') as file:
        file.write(data)

# Beispielnutzung:
if __name__ == '__main__':
    # Der Pfad zur .dat-Datei
    filename = r'C:\Program Files\VstPlugins\jup-6.dat'
    
    # Überprüfen, ob die Datei existiert
    if os.path.exists(filename):
        # Binärdaten aus Datei lesen
        data = read_binary_file(filename)
        
        # Beispieldaten ausgeben (die ersten 20 Bytes anzeigen, um zu sehen, was die Datei enthält)
        print(f"Originaldaten (erste 20 Bytes): {data[:20]}")
        
        # Die Binärdaten modifizieren: z.B. an Position 8 (Offset 8) den Wert durch 12345 ersetzen
        modified_data = modify_binary_data(data, 8, 12345)
        
        # Die modifizierten Daten wieder speichern
        save_binary_file(filename, modified_data)
        
        print("Datei erfolgreich modifiziert und gespeichert!")
    else:
        print(f"Datei {filename} nicht gefunden!")
