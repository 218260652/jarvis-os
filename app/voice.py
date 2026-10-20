"""Short, explicit push-to-talk capture. Audio stays on this machine."""
from pathlib import Path
import subprocess
import tempfile
import wave


def listen():
    from pocketsphinx import Decoder
    root = Path('/usr/share/pocketsphinx/model/en-us')
    config = Decoder.default_config()
    config.set_string('-hmm', str(root / 'en-us'))
    config.set_string('-lm', str(root / 'en-us.lm.bin'))
    config.set_string('-dict', str(root / 'cmudict-en-us.dict'))
    config.set_string('-logfn', '/dev/null')
    decoder = Decoder(config)
    with tempfile.TemporaryDirectory(prefix='jarvis-mic-') as directory:
        audio = Path(directory) / 'speech.wav'
        result = subprocess.run(['arecord', '-q', '-D', 'default', '-f', 'S16_LE',
                                 '-r', '16000', '-c', '1', '-d', '6', str(audio)],
                                capture_output=True, timeout=12)
        if result.returncode:
            raise RuntimeError('Microphone capture failed. Check Sound settings and input device.')
        with wave.open(str(audio), 'rb') as wav:
            decoder.start_utt()
            decoder.process_raw(wav.readframes(wav.getnframes()), False, True)
            decoder.end_utt()
        hypothesis = decoder.hyp()
        if not hypothesis or not hypothesis.hypstr.strip():
            raise RuntimeError('No speech understood. Try again or type your command.')
        return hypothesis.hypstr


def speak(text):
    # stdin prevents text beginning with '-' from becoming a command option.
    subprocess.run(['espeak-ng', '-s', '165', '-v', 'en', '--stdin'],
                   input=text[:4000], text=True, capture_output=True, timeout=180)
