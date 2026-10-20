"""Capture real VM screenshots. This does not automatically certify a working OS."""
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image


def main():
    iso = Path(sys.argv[1]).resolve(strict=True)
    out = Path('boot-evidence').resolve()
    out.mkdir(exist_ok=True)
    sock = out / 'qmp.sock'
    command = ['qemu-system-x86_64', '-m', '2048', '-smp', '2', '-cpu', 'core2duo', '-boot', 'd',
               '-cdrom', str(iso), '-display', 'none', '-nic', 'user',
               '-serial', 'file:' + str(out / 'serial.log'),
               '-qmp', f'unix:{sock},server=on,wait=off', '-no-reboot']
    (out / 'README.txt').write_text(
        'Legacy BIOS / Core 2 Duo emulation / 2 GB RAM / QEMU software emulation.\n'
        'No writable hard disk is attached.\n'
        'Screenshots need human review. Successful capture is NOT a boot-test pass.\n'
        'App versions and Chrome/VLC launch screenshots are attempted. No audio, Windows app, installer, physical hardware or AI test is performed here.\n')
    with (out / 'qemu.log').open('w') as log:
        proc = subprocess.Popen(command, stdout=log, stderr=log)
        try:
            for _ in range(60):
                if proc.poll() is not None:
                    raise RuntimeError('QEMU exited before its monitor was ready')
                if sock.exists():
                    break
                time.sleep(1)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
                conn.settimeout(30)
                conn.connect(str(sock))
                stream = conn.makefile('rwb', buffering=0)
                stream.readline()
                def qmp(name, args=None):
                    request = {'execute': name}
                    if args:
                        request['arguments'] = args
                    stream.write((json.dumps(request) + '\n').encode())
                    while True:
                        reply = json.loads(stream.readline())
                        if 'error' in reply:
                            raise RuntimeError(reply['error'])
                        if 'return' in reply:
                            return reply['return']
                qmp('qmp_capabilities')
                # The live ISO menu waits for input; explicitly select Live system.
                time.sleep(20)
                qmp('send-key', {'keys': [{'type': 'qcode', 'data': 'ret'}]})
                for n in range(1, 4):
                    time.sleep(120)
                    ppm = out / f'boot-{n*120}s.ppm'
                    qmp('screendump', {'filename': str(ppm)})
                    with Image.open(ppm) as im:
                        im.save(ppm.with_suffix('.png'))
                    ppm.unlink()
                    print(f'Screenshot captured at {n*120} seconds', flush=True)
                def capture(name):
                    ppm = out / (name + '.ppm')
                    qmp('screendump', {'filename': str(ppm)})
                    with Image.open(ppm) as im:
                        im.save(ppm.with_suffix('.png'))
                    ppm.unlink()
                def keys(*codes):
                    qmp('send-key', {'keys': [{'type': 'qcode', 'data': c} for c in codes], 'hold-time': 30})
                    time.sleep(0.06)
                punctuation = {' ': ('spc',), '-': ('minus',), '/': ('slash',),
                    '.': ('dot',), ';': ('semicolon',), "'": ('apostrophe',),
                    '|': ('shift', 'backslash'), '>': ('shift', 'dot'),
                    '&': ('shift', '7'), ':': ('shift', 'semicolon'),
                    '(': ('shift', '9'), ')': ('shift', '0'),
                    '_': ('shift', 'minus')}
                def type_command(text):
                    for char in text:
                        if char in punctuation:
                            keys(*punctuation[char])
                        elif char.isupper():
                            keys('shift', char.lower())
                        else:
                            keys(char)
                    keys('ret')
                # Use the logged-in live desktop, with no files or credentials supplied.
                keys('ctrl', 'alt', 't')
                time.sleep(8)
                type_command("id; google-chrome-stable --version; vlc --version | head -n 1; wine --version; command -v jarvis pocketsphinx_continuous; python3 -c 'import tkinter; print(tkinter.TkVersion)'")
                time.sleep(8)
                capture('runtime-report')
                type_command('google-chrome-stable --no-first-run about:blank >/tmp/chrome.log 2>&1 &')
                time.sleep(20)
                capture('chrome-launch')
                keys('ctrl', 'alt', 't')
                time.sleep(5)
                type_command('vlc >/tmp/vlc.log 2>&1 &')
                time.sleep(15)
                capture('vlc-launch')
                qmp('quit')
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=20)
            sock.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
