import os

from dx7utils.common import debug_print, identify_instrument


def format_name(name):
    return ''.join(c for c in name.decode('ascii', 'ignore') if c.isalnum())


def extract_patch_names(file_path):
    patch_names = []
    instrument_type = "Unknown"
    try:
        file_size = os.path.getsize(file_path)
        instrument_type = identify_instrument(file_size)

        with open(file_path, 'rb') as f:
            f.read(6)

            if instrument_type in ["Yamaha DX1 or DX5", "Yamaha DX7IIFD"]:
                num_voices = 64
            elif instrument_type == "Yamaha TX816":
                num_voices = 256
            else:
                num_voices = 32

            for voice_number in range(num_voices):
                f.read(6 * 17)
                f.read(16)
                name_data = f.read(10)
                patch_name = format_name(name_data)
                patch_names.append(patch_name.strip())

        debug_print(f"Extrahierte Patch-Namen aus {file_path}: {patch_names}")
    except Exception as e:
        debug_print(f"Fehler beim Lesen der Datei {file_path}: {e}")

    return patch_names, instrument_type
