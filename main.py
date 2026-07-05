import importlib
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

TOOLS = [
    ("⚙  Konfiguration", "src.config", "gui", None),
    ("🔍  Patch Suche", "src.PatchSearchApp", "gui", None),
    ("───", "", "", None),
    ("🎛  MIDI Fader", "src.ui", "gui", "midi"),
    ("💾  MIDI Backup", "src.ui", "gui", "midibackup"),
    ("🐛  MIDI Debug", "src.ui", "gui", "mididebug"),
    ("📋  Patch Suche (CLI)", "src.patchsearchercmd", "cli", None),
    ("📖  SysEx lesen", "src.ui", "gui", "readsysex"),
    ("📤  SysEx senden", "src.ui", "gui", "sendsysex"),
    ("🔌  MIDI Ports", "src.ui", "gui", "ports"),
]

TOOL_MAP: dict[str, tuple] = {}
for t, m, k, a in TOOLS:
    if m:
        TOOL_MAP.setdefault(m, (t, k, a))


def run_tool(module_name, kind, tool_arg=None):
    try:
        if kind == "gui":
            mod = importlib.import_module(module_name)
            if tool_arg:
                mod.main(tool_arg)
            else:
                mod.main()
        else:
            subprocess.Popen(
                [sys.executable, module_name],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
    except Exception as e:
        messagebox.showerror("Fehler", f"{module_name}: {e}")


class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DX7 Utils")
        self.root.geometry("420x540")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        tk.Label(root, text="DX7 Utils", font=("Segoe UI", 18, "bold"),
                 bg="#f0f0f0", fg="#333").pack(pady=(16, 4))
        tk.Label(root, text="Yamaha DX7 Werkzeuge",
                 font=("Segoe UI", 10), bg="#f0f0f0", fg="#666").pack(pady=(0, 12))

        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(padx=20, pady=(0, 12), fill=tk.BOTH, expand=True)

        for title, module, kind, arg in TOOLS:
            if title == "───":
                sep = tk.Frame(frame, height=1, bg="#ccc")
                sep.pack(fill=tk.X, pady=6)
                continue
            btn = tk.Button(
                frame,
                text=title,
                anchor="w",
                font=("Segoe UI", 11),
                bg="#fff",
                fg="#333",
                relief=tk.FLAT,
                bd=1,
                highlightthickness=0,
                padx=12,
                pady=8,
                cursor="hand2",
                command=lambda m=module, k=kind, a=arg: run_tool(m, k, a),
            )
            btn.pack(fill=tk.X, pady=3)

        tk.Button(
            root, text="Beenden", font=("Segoe UI", 10),
            command=root.quit, bg="#e0e0e0", relief=tk.FLAT, padx=20, pady=4,
        ).pack(pady=(0, 12))


def main():
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
        if module_name in TOOL_MAP:
            _, kind, arg = TOOL_MAP[module_name]
            mod = importlib.import_module(module_name)
            if kind == "gui":
                if arg:
                    mod.main(arg)
                else:
                    mod.main()
            else:
                run_tool(module_name, kind, arg)
        else:
            print(f"Unbekanntes Werkzeug: {module_name}", file=sys.stderr)
            print("Verfügbar:", ", ".join(sorted(TOOL_MAP)))
            sys.exit(1)
        return

    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
