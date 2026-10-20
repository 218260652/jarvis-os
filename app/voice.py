"""Short, explicit push-to-talk capture. Audio stays on this machine."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def parse_pocketsphinx_output(text):
    """Keep the last hypothesis. Ignore PocketSphinx log lines."""
    hypothesis = ''
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(('INFO:', 'ERROR:', 'DEBUG:', 'FATAL:', 'WARN:')):
            continue
        line = re.sub(r'^\d+:\s*', '', line)
        if line and not line.startswith('-'):
            hypothesis = line
    return hypothesis


def listen():
    binary = shutil.which('pocketsphinx_continuous')
    if not binary:
        raise RuntimeError(
            'Offline speech recognition is not installed. The pocketsphinx package is required.')
    root = Path('/usr/share/pocketsphinx/model/en-us')
    hmm = root / 'en-us'
    language = root / 'en-us.lm.bin'
    dictionary = root / 'cmudict-en-us.dict'
    missing = [str(path) for path in (hmm, language, dictionary) if not path.exists()]
    if missing:
        raise RuntimeError('English speech model is missing. Install pocketsphinx-en-us.')
    with tempfile.TemporaryDirectory(prefix='jarvis-mic-') as directory:
        audio = Path(directory) / 'speech.wav'
        recorded = subprocess.run(
            ['arecord', '-q', '-D', 'default', '-f', 'S16_LE', '-r', '16000', '-c', '1', '-d', '6', str(audio)],
            capture_output=True, timeout=12)
        if recorded.returncode:
            raise RuntimeError('Microphone capture failed. Check Sound settings and input device.')
        recognised = subprocess.run(
            [binary, '-infile', str(audio), '-hmm', str(hmm), '-lm', str(language),
             '-dict', str(dictionary), '-logfn', '/dev/null'],
            capture_output=True, text=True, timeout=30)
    if recognised.returncode:
        detail = (recognised.stderr or recognised.stdout or '').strip().splitlines()
        extra = f' {detail[-1]}' if detail else ''
        raise RuntimeError('Speech recognition failed.' + extra)
    hypothesis = parse_pocketsphinx_output(recognised.stdout)
    if not hypothesis:
        raise RuntimeError('No speech understood. Try again or type your command.')
    return hypothesis


def speak(text):
    # stdin prevents text beginning with '-' from becoming a command option.
    subprocess.run(['espeak-ng', '-s', '165', '-v', 'en', '--stdin'],
                   input=text[:4000], text=True, capture_output=True, timeout=180)
