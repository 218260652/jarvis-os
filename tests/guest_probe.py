"""Diagnostic helper for a disposable VM only; not included in the OS overlay."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

subprocess.run(['stty', '-F', '/dev/ttyS0', '115200', 'raw', '-echo', 'clocal'], check=True)
serial = open('/dev/ttyS0', 'w', buffering=1)
sys.stdout = serial
sys.stderr = serial
print('PROBE_STARTED', flush=True)

def run(args, **kwargs):
    return subprocess.run(args, capture_output=True, text=True, timeout=kwargs.pop('timeout', 30), **kwargs)

try:
    session = None
    for _ in range(120):
        p = run(['pgrep', '-u', 'jarvis', '-x', 'xfce4-session'])
        if p.returncode == 0:
            pid = p.stdout.splitlines()[0]
            fields = Path('/proc/' + pid + '/environ').read_bytes().split(b'\0')
            session = dict(item.decode(errors='replace').split('=', 1) for item in fields if b'=' in item)
            if session.get('DISPLAY'):
                break
        time.sleep(2)
    if not session or not session.get('DISPLAY'):
        raise RuntimeError('Xfce session not ready')
    print('SESSION_DISPLAY=' + session['DISPLAY'], flush=True)
    print('FIRMWARE_MODE=' + ('uefi' if Path('/sys/firmware/efi').exists() else 'bios'), flush=True)
    print('MEMORY_BEFORE_APPS:\n' + Path('/proc/meminfo').read_text(), flush=True)
    env = dict(os.environ, DEBIAN_FRONTEND='noninteractive')
    installed = run(['apt-get', '-qq', '-o', 'Acquire::Retries=3', 'install', '-y',
                     '--no-install-recommends', 'xdotool'], env=env, timeout=180)
    print('AUTOMATION_DEPENDENCY_EXIT=' + str(installed.returncode), flush=True)
    if installed.returncode:
        raise RuntimeError(installed.stderr)

    def user(args, timeout=30):
        return run(['/usr/sbin/runuser', '-u', 'jarvis', '--', *args], env=session, timeout=timeout)

    def launch(args, log):
        fd = open('/tmp/' + log, 'w')
        return subprocess.Popen(['/usr/sbin/runuser', '-u', 'jarvis', '--', *args],
                                env=session, cwd='/home/jarvis',
                                stdin=subprocess.DEVNULL, stdout=fd, stderr=fd)

    def window(pattern):
        for _ in range(60):
            found = user(['xdotool', 'search', '--name', pattern])
            if found.returncode == 0 and found.stdout.strip():
                return found.stdout.splitlines()[-1]
            time.sleep(2)
        raise RuntimeError('Window not found: ' + pattern)

    def activate(wid):
        result = user(['xdotool', 'windowactivate', '--sync', wid], timeout=20)
        print('ACTIVATE=' + str(result.returncode), flush=True)
        time.sleep(10)

    def capture(name):
        print('CAPTURE:' + name, flush=True)
        time.sleep(8)

    assistant = window('Desktop companion')
    activate(assistant)
    print('ASSISTANT_WINDOW=' + user(['xdotool', 'getwindowname', assistant]).stdout.strip(), flush=True)
    capture('assistant-ready')
    user(['xdotool', 'windowminimize', assistant])
    time.sleep(20)
    print('DESKTOP_PROPERTIES:\n' + user(['xfconf-query', '-c', 'xfce4-desktop', '-lv']).stdout, flush=True)
    print('DESKTOP_SETUP:\n' + user(['/usr/local/bin/jarvis-desktop-setup']).stdout, flush=True)
    time.sleep(10)
    capture('desktop-wallpaper')
    menu = launch(['xfce4-popup-whiskermenu'], 'probe-menu.log')
    time.sleep(5)
    capture('app-menu')
    user(['xdotool', 'key', 'Escape'])

    chrome = launch(['google-chrome-stable', '--no-first-run', 'about:blank'], 'probe-chrome.log')
    chrome_window = window('Google Chrome')
    activate(chrome_window)
    time.sleep(20)
    print('CHROME_WINDOW=' + user(['xdotool', 'getwindowname', chrome_window]).stdout.strip(), flush=True)
    capture('chrome-launch')
    user(['xdotool', 'windowminimize', chrome_window])

    vlc = launch(['vlc'], 'probe-vlc.log')
    vlc_window = window('VLC media player')
    activate(vlc_window)
    time.sleep(15)
    print('VLC_WINDOW=' + user(['xdotool', 'getwindowname', vlc_window]).stdout.strip(), flush=True)
    capture('vlc-launch')

    for args in [['id'], ['google-chrome-stable', '--version'], ['vlc', '--version'], ['wine', '--version']]:
        r = user(args)
        print('VERSION ' + repr(args) + '\n' + r.stdout[:2000] + r.stderr[:500], flush=True)
    print('MEMORY_WITH_APPS:\n' + Path('/proc/meminfo').read_text(), flush=True)
    print('PROBE_RESULT=' + json.dumps({'assistant_window': bool(assistant),
          'chrome_window': bool(chrome_window), 'vlc_window': bool(vlc_window)}), flush=True)
    print('PROBE_COMPLETE', flush=True)
except Exception as exc:
    print('PROBE_ERROR=' + repr(exc), flush=True)
    raise
