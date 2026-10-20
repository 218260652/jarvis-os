#!/usr/bin/env python3
"""Native, low-dependency J.A.R.V.I.S. desktop application."""
import math
import os
import queue
import threading
import tkinter as tk
from tkinter import messagebox
from core import COMMANDS, parse_command, execute, ask_ai
from voice import listen, speak

BG, PANEL, GOLD, CYAN, TEXT = '#070d16', '#101d2c', '#ffbf48', '#55d9ff', '#e5edf7'


class Jarvis(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('J.A.R.V.I.S. • Desktop companion — Development preview')
        self.geometry('780x680')
        self.minsize(650, 580)
        self.configure(bg=BG)
        self.events = queue.Queue()
        self.key = os.environ.pop('OPENAI_API_KEY', '')
        self.model = os.environ.get('JARVIS_MODEL', '')
        self.busy = False
        self.speaking = threading.Event()
        self.speech_lock = threading.Lock()
        self.phase = 0
        self.animations = tk.BooleanVar(value=False)
        self.speech = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value='LOCAL MODE  •  Microphone off')
        tk.Label(self, text='J.A.R.V.I.S.', font=('DejaVu Sans', 25, 'bold'),
                 bg=BG, fg=GOLD).pack(pady=(18, 3))
        tk.Label(self, text='YOUR VOICE. YOUR DESKTOP.', font=('DejaVu Sans', 10),
                 bg=BG, fg=CYAN).pack()
        self.orb = tk.Canvas(self, width=360, height=210, bg=BG, highlightthickness=0)
        self.orb.pack(pady=3)
        tk.Label(self, textvariable=self.status, bg=BG, fg=CYAN).pack()
        row = tk.Frame(self, bg=BG)
        row.pack(pady=10)
        self.button(row, 'Files', lambda: self.local('open files')).pack(side='left', padx=3)
        self.button(row, 'Browser', lambda: self.local('open browser')).pack(side='left', padx=3)
        self.button(row, 'Windows apps', lambda: self.local('open windows app')).pack(side='left', padx=3)
        self.button(row, 'AI Connection', self.connection).pack(side='left', padx=3)
        self.history = tk.Text(self, height=9, wrap='word', bg=PANEL, fg=TEXT,
                               relief='flat', padx=14, pady=12, font=('DejaVu Sans', 10))
        self.history.pack(fill='both', expand=True, padx=20, pady=5)
        self.history.configure(state='disabled')
        self.add('J.A.R.V.I.S.', 'Ready. Type a desktop command or press Listen. Voice recognition stays local. '
                 'Use Ask AI only when you want to send your message online. Type help for commands.')
        self.entry = tk.Entry(self, bg=PANEL, fg=TEXT, insertbackground=GOLD,
                              relief='flat', font=('DejaVu Sans', 12))
        self.entry.pack(fill='x', padx=20, ipady=10, pady=7)
        self.entry.bind('<Return>', lambda e: self.local())
        controls = tk.Frame(self, bg=BG)
        controls.pack(pady=(0, 8))
        self.button(controls, 'Run command', self.local).pack(side='left', padx=4)
        self.listen_button = self.button(controls, 'Listen · 6 seconds', self.capture)
        self.listen_button.pack(side='left', padx=4)
        self.button(controls, 'Ask AI ↗', self.chat).pack(side='left', padx=4)
        for label, value in [('Speak replies', self.speech), ('Animate orb', self.animations)]:
            tk.Checkbutton(controls, text=label, variable=value, bg=BG, fg=TEXT,
                           selectcolor=PANEL, activebackground=BG).pack(side='left', padx=4)
        self.after(100, self.poll)
        self.draw_orb()

    def button(self, parent, label, callback):
        return tk.Button(parent, text=label, command=callback, bg=PANEL, fg=CYAN,
                         activebackground='#203a50', activeforeground=TEXT,
                         relief='flat', padx=10, pady=8)

    def draw_orb(self):
        self.orb.delete('all')
        cx, cy = 180, 106
        for radius, color in [(91, '#74451c'), (85, GOLD), (77, '#ba772a'), (32, GOLD)]:
            self.orb.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, outline=color, width=2)
        for i in range(7):
            angle = math.radians(i * 26 + self.phase)
            width = max(8, abs(math.cos(angle)) * 78)
            self.orb.create_oval(cx-width, cy-78, cx+width, cy+78, outline='#ae742c')
        for i in range(64):
            a = i * math.tau / 64 + math.radians(self.phase)
            radius = 48 + 33 * abs(math.sin(i * 2.7))
            x, y = cx + math.cos(a)*radius, cy + math.sin(a)*radius
            self.orb.create_oval(x-1, y-1, x+1, y+1, fill=GOLD, outline='')
        self.orb.create_oval(cx-9, cy-9, cx+9, cy+9, fill=GOLD, outline='#ffe6ab', width=3)
        if self.animations.get():
            self.phase = (self.phase + 2) % 360
        self.after(150 if self.animations.get() else 750, self.draw_orb)

    def add(self, speaker, text):
        self.history.configure(state='normal')
        self.history.insert('end', f'{speaker}: {text}\n\n')
        self.history.see('end')
        self.history.configure(state='disabled')

    def reply(self, text):
        self.add('J.A.R.V.I.S.', text)
        if self.speech.get():
            def run():
                with self.speech_lock:
                    self.speaking.set()
                    try:
                        speak(text)
                    except Exception:
                        self.events.put(('speech_error', 'Speech output unavailable. Check sound and espeak-ng.'))
                    finally:
                        self.speaking.clear()
            threading.Thread(target=run, daemon=True).start()

    def local(self, text=None):
        text = text or self.entry.get().strip()
        if not text:
            return
        self.add('You', text)
        self.entry.delete(0, 'end')
        if text.lower().strip() == 'help':
            self.reply('Commands: ' + ', '.join(COMMANDS))
            return
        action = parse_command(text)
        if not action:
            self.reply('Command not recognised. Type help. For a general question use Ask AI.')
            return
        approved = not action.confirm or messagebox.askyesno(
            'Confirm computer action', action.label + '? Save your work first.', parent=self)
        if not approved:
            self.reply('Cancelled.')
            return
        try:
            process = execute(action, approved)
            self.reply(action.label + ': request started.')
            def watch():
                code = process.wait()
                if code:
                    self.events.put(('action_error', f'{action.label} failed (exit {code}).'))
            threading.Thread(target=watch, daemon=True).start()
        except Exception as exc:
            self.reply(str(exc))

    def job(self, fn, kind, status):
        if self.busy:
            return
        self.busy = True
        self.status.set(status)
        self.listen_button.configure(state='disabled')
        def worker():
            try:
                self.events.put((kind, fn()))
            except Exception as exc:
                self.events.put(('error', str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def capture(self):
        if self.speaking.is_set():
            self.add('System', 'Wait until J.A.R.V.I.S. finishes speaking, then press Listen.')
            return
        self.job(listen, 'transcript', 'LISTENING  •  Speak now for up to 6 seconds')

    def chat(self):
        text = self.entry.get().strip()
        if not text or self.busy:
            return
        if not self.key or not self.model:
            self.connection()
            return
        self.add('You → AI', text)
        self.entry.delete(0, 'end')
        key, model = self.key, self.model
        self.job(lambda: ask_ai(text, key, model), 'answer', 'AI REQUEST  •  Sending this message online')

    def poll(self):
        while not self.events.empty():
            kind, text = self.events.get_nowait()
            if kind in {'speech_error', 'action_error'}:
                self.add('System', text)
                continue
            self.busy = False
            self.listen_button.configure(state='normal')
            self.status.set('READY  •  Microphone off')
            if kind == 'transcript':
                self.entry.delete(0, 'end')
                self.entry.insert(0, text)
                self.add('Heard', text)
                if parse_command(text):
                    # The allowlist applies to voice too; power actions still need a click.
                    self.local(text)
                else:
                    self.reply('Review the words, then choose Run command or Ask AI.')
            else:
                self.reply(text)
        self.after(100, self.poll)

    def connection(self):
        win = tk.Toplevel(self)
        win.title('J.A.R.V.I.S. • AI Connection')
        win.configure(bg=BG)
        win.transient(self)
        tk.Label(win, text='Optional OpenAI API connection', bg=BG, fg=GOLD,
                 font=('DejaVu Sans', 14)).pack(padx=20, pady=15)
        tk.Label(win, text='Only Ask AI sends your entered text online.\n'
                 'No files, audio or screenshots are sent.\n'
                 'Credentials stay in memory until J.A.R.V.I.S. closes.\n'
                 'API usage may cost money. This is not a ChatGPT login.',
                 bg=BG, fg=TEXT, justify='left').pack(padx=20)
        tk.Label(win, text='API key', bg=BG, fg=CYAN).pack(pady=(12, 0))
        key = tk.Entry(win, width=48, show='•')
        key.insert(0, self.key)
        key.pack(padx=20)
        tk.Label(win, text='Model ID available to your API account', bg=BG, fg=CYAN).pack(pady=(12, 0))
        model = tk.Entry(win, width=48)
        model.insert(0, self.model)
        model.pack(padx=20)
        def save():
            self.key, self.model = key.get().strip(), model.get().strip()
            self.status.set('AI CONFIGURED — UNTESTED  •  Microphone off')
            win.destroy()
        def disconnect():
            self.key = self.model = ''
            self.status.set('LOCAL MODE  •  Microphone off')
            win.destroy()
        self.button(win, 'Use for this session', save).pack(pady=10)
        self.button(win, 'Disconnect', disconnect).pack(pady=(0, 12))


if __name__ == '__main__':
    Jarvis().mainloop()
