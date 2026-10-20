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
    command = ['qemu-system-x86_64', '-m', '2048', '-smp', '2', '-boot', 'd',
               '-cdrom', str(iso), '-display', 'none', '-nic', 'user',
               '-serial', 'file:' + str(out / 'serial.log'),
               '-qmp', f'unix:{sock},server=on,wait=off', '-no-reboot']
    (out / 'README.txt').write_text(
        'Legacy BIOS / 2 GB RAM / QEMU software emulation.\n'
        'No writable hard disk is attached.\n'
        'Screenshots need human review. Successful capture is NOT a boot-test pass.\n'
        'No audio, Windows app, installer, hardware or AI test is performed here.\n')
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
                for n in range(1, 4):
                    time.sleep(120)
                    ppm = out / f'boot-{n*120}s.ppm'
                    qmp('screendump', {'filename': str(ppm)})
                    with Image.open(ppm) as im:
                        im.save(ppm.with_suffix('.png'))
                    ppm.unlink()
                    print(f'Screenshot captured at {n*120} seconds', flush=True)
                qmp('quit')
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=20)
            sock.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
