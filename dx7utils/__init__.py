import sys
if sys.platform == 'win32':
    import colorama
    colorama.just_fix_windows_console()

from dx7utils.common import debug_print, clear_console_line, load_config, find_sysex_files, identify_instrument
from dx7utils.sysex import extract_patch_names, format_name
