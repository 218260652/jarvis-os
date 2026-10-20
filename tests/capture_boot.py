"""Boot a disposable live VM and collect readiness-based diagnostic evidence."""
import functools
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from PIL import Image

def main():
    iso = Path(sys.argv[1]).resolve(strict=True)
    uefi = os.environ.get('JARVIS_BOOT_MODE', 'bios') == 'uefi'
    out = Path('boot-evidence').resolve()
    out.mkdir(exist_ok=True)
    sock = out / 'qmp.sock'
    serial_path = out / 'serial.log'
    (out / 'README.txt').write_text(
        ('UEFI' if uefi else 'Legacy BIOS') + ', Core 2 Duo emulation, 2 GB RAM. No writable hard disk.\n'
        'A diagnostic helper is injected into this disposable VM through its normal\n'
        'live-user console. xdotool is installed for test automation only.\n'
        'No AI key, personal files or account sign-in are supplied.\n')
    with tempfile.TemporaryDirectory(prefix='jarvis-probe-host-') as directory:
        shutil.copy('tests/guest_probe.py', Path(directory) / 'probe.py')
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        command = ['qemu-system-x86_64', '-m', '2048', '-smp', '2', '-cpu', 'core2duo',
                   '-boot', 'd', '-cdrom', str(iso), '-display', 'none', '-nic', 'user',
                   '-serial', 'file:' + str(serial_path), '-qmp',
                   f'unix:{sock},server=on,wait=off', '-no-reboot']
        if uefi:
            code = Path('/usr/share/OVMF/OVMF_CODE_4M.fd')
            variables = Path(directory) / 'OVMF_VARS.fd'
            shutil.copy('/usr/share/OVMF/OVMF_VARS_4M.fd', variables)
            command += ['-drive', f'if=pflash,format=raw,readonly=on,file={code}',
                        '-drive', f'if=pflash,format=raw,file={variables}']
        with (out / 'qemu.log').open('w') as log:
            proc = subprocess.Popen(command, stdout=log, stderr=log)
            try:
                for _ in range(60):
                    if proc.poll() is not None:
                        raise RuntimeError('QEMU exited')
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
                    def capture(name):
                        ppm = out / (name + '.ppm')
                        qmp('screendump', {'filename': str(ppm)})
                        with Image.open(ppm) as im:
                            im.save(ppm.with_suffix('.png'))
                        ppm.unlink()
                        return out / (name + '.png')
                    def keys(*codes):
                        qmp('send-key', {'keys': [{'type': 'qcode', 'data': c} for c in codes], 'hold-time': 30})
                        time.sleep(0.08)
                    punctuation = {' ': ('spc',), '-': ('minus',), '/': ('slash',),
                                   '.': ('dot',), ':': ('shift', 'semicolon'),
                                   ';': ('semicolon',)}
                    def type_text(text):
                        for char in text:
                            if char in punctuation:
                                keys(*punctuation[char])
                            elif char.isupper():
                                keys('shift', char.lower())
                            else:
                                keys(char)
                        keys('ret')
                    def screen_text():
                        path = capture('console-status')
                        result = subprocess.run(['tesseract', str(path), 'stdout', '--psm', '6'],
                                                capture_output=True, text=True, timeout=30)
                        return result.stdout

                    qmp('qmp_capabilities')
                    time.sleep(20)
                    keys('ret')
                    time.sleep(120)
                    capture('boot-120s')
                    keys('ctrl', 'alt', 'f2')
                    time.sleep(8)
                    ready = False
                    for _ in range(12):
                        text = screen_text()
                        print('CONSOLE=' + text[-1200:], flush=True)
                        lower = text.lower()
                        if 'login:' in lower:
                            type_text('jarvis')
                            time.sleep(3)
                            text = screen_text()
                            if 'password' in text.lower():
                                type_text('live')
                                time.sleep(5)
                            continue
                        if 'password' in lower:
                            type_text('live')
                            time.sleep(5)
                            continue
                        if 'jarvis@' in lower or ('jarvis-os' in lower and '$' in lower):
                            ready = True
                            break
                        time.sleep(5)
                    if not ready:
                        raise RuntimeError('Live console login not ready')
                    type_text('curl -fsS http://10.0.2.2:8765/probe.py -o /tmp/jarvis-probe.py; sudo -n python3 /tmp/jarvis-probe.py')
                    started = time.monotonic()
                    switched = False
                    captured = set()
                    complete = False
                    while time.monotonic() - started < 600:
                        text = serial_path.read_text(errors='replace') if serial_path.exists() else ''
                        if 'PROBE_STARTED' in text and not switched:
                            keys('ctrl', 'alt', 'f7')
                            switched = True
                            time.sleep(3)
                        for name in re.findall(r'^CAPTURE:([a-z-]+)', text, re.M):
                            if name not in captured:
                                capture(name)
                                captured.add(name)
                                print('CAPTURED=' + name, flush=True)
                        if 'PROBE_ERROR=' in text:
                            print(text, flush=True)
                            raise RuntimeError('Guest diagnostic failed')
                        if 'PROBE_COMPLETE' in text:
                            complete = True
                            break
                        time.sleep(1)
                    print(serial_path.read_text(errors='replace')[-25000:], flush=True)
                    if not complete:
                        capture('probe-timeout')
                        raise RuntimeError('Guest diagnostic timeout')
                    if uefi and 'FIRMWARE_MODE=uefi' not in serial_path.read_text(errors='replace'):
                        raise RuntimeError('Guest did not confirm UEFI boot')
                    qmp('quit')
            finally:
                if proc.poll() is None:
                    proc.terminate()
                proc.wait(timeout=20)
                sock.unlink(missing_ok=True)
                server.shutdown()

if __name__ == '__main__':
    main()
