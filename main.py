import importlib
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

TOOLS = [
    ("⚙  Konfiguration", "src.config", "gui"),
    ("🔍  Patch Suche (GUI)", "src.PatchSearchApp", "gui"),
    ("───", "", ""),
    ("🎛  MIDI Fader", "src.midi", "cli"),
    ("💾  MIDI Backup", "src.midibackup", "cli"),
    ("🐛  MIDI Debug", "src.mididebug", "cli"),
    ("📋  Patch Suche (CLI)", "src.patchsearchercmd", "cli"),
    ("📖  SysEx lesen", "src.readsysex", "cli"),
    ("📤  SysEx senden", "src.sendsysex", "cli"),
    ("🔌  MIDI Ports", "src.ports", "cli"),
]

TOOL_MAP = {m: (t, k) for t, m, k in TOOLS if m}


def run_tool(module_name, kind):
    try:
        if kind == "gui":
            mod = importlib.import_module(module_name)
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

        for title, module, kind in TOOLS:
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
                command=lambda m=module, k=kind: run_tool(m, k),
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
            mod = importlib.import_module(module_name)
            mod.main()
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
