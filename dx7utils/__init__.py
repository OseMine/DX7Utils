import sys

if sys.platform == 'win32':
    import colorama
    colorama.just_fix_windows_console()

from dx7utils.common import (
    clear_console_line as clear_console_line,
)
from dx7utils.common import (
    debug_print as debug_print,
)
from dx7utils.common import (
    find_sysex_files as find_sysex_files,
)
from dx7utils.common import (
    identify_instrument as identify_instrument,
)
from dx7utils.common import (
    load_config as load_config,
)
from dx7utils.sysex import (
    extract_patch_names as extract_patch_names,
)
from dx7utils.sysex import (
    format_name as format_name,
)
