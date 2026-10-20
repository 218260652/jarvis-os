#!/usr/bin/env python3
"""Explicitly confirmed Windows application launcher; Wine is not a sandbox."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from core import windows_command


def main():
    root = tk.Tk()
    root.withdraw()
    if not shutil.which('wine'):
        messagebox.showerror('Windows apps', 'Wine is not installed.')
        root.destroy()
        return 1
    path = sys.argv[1] if len(sys.argv) > 1 else filedialog.askopenfilename(
        title='Choose a Windows program', filetypes=[('Windows programs', '*.exe *.EXE *.msi *.MSI')])
    if not path:
        root.destroy()
        return 0
    try:
        command = windows_command(path)
        if not messagebox.askyesno('Run Windows program?',
                f'{Path(path).name}\n\nOnly run software you trust. Wine is not a sandbox; '
                'this program can access your files. Compatibility is not guaranteed.\n\nRun it?'):
            root.destroy()
            return 0
        state = Path.home() / '.local/state/jarvis'
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        environment = dict(os.environ, WINEPREFIX=str(Path.home() / '.local/share/jarvis-wine'))
        (Path.home() / '.local/share').mkdir(parents=True, exist_ok=True)
        log_path = state / 'wine.log'
        fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, 'a') as log:
            subprocess.Popen(command, cwd=str(Path(path).resolve().parent), env=environment,
                             stdin=subprocess.DEVNULL, stdout=log, stderr=log)
        messagebox.showinfo('Windows apps', 'Launch requested. First launch can take time.\n'
                            f'If it fails, inspect {log_path}')
    except Exception as exc:
        messagebox.showerror('Windows apps', str(exc))
        root.destroy()
        return 1
    root.destroy()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
