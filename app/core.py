"""J.A.R.V.I.S.: deliberately bounded desktop actions; never executes AI-generated code."""
from dataclasses import dataclass
from pathlib import Path
import json
import re
import shutil
import subprocess
import urllib.request
import urllib.error


@dataclass(frozen=True)
class Action:
    label: str
    argv: tuple[str, ...]
    confirm: bool = False


COMMANDS = {
    'open browser': Action('Open Chrome', ('google-chrome-stable',)),
    'open chrome': Action('Open Chrome', ('google-chrome-stable',)),
    'open files': Action('Open files', ('thunar',)),
    'open settings': Action('Open settings', ('xfce4-settings-manager',)),
    'open terminal': Action('Open terminal', ('xfce4-terminal',)),
    'open documents': Action('Open documents', ('xdg-open', str(Path.home() / 'Documents'))),
    'open downloads': Action('Open downloads', ('xdg-open', str(Path.home() / 'Downloads'))),
    'open calculator': Action('Open calculator', ('galculator',)),
    'open text editor': Action('Open text editor', ('mousepad',)),
    'open media player': Action('Open VLC', ('vlc',)),
    'open vlc': Action('Open VLC', ('vlc',)),
    'open windows app': Action('Choose Windows app', ('jarvis-windows',)),
    'volume up': Action('Increase volume', ('pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%')),
    'volume down': Action('Decrease volume', ('pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%')),
    'mute': Action('Mute audio', ('pactl', 'set-sink-mute', '@DEFAULT_SINK@', '1')),
    'unmute': Action('Unmute audio', ('pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0')),
    'brightness up': Action('Increase brightness', ('brightnessctl', 'set', '10%+')),
    'brightness down': Action('Decrease brightness', ('brightnessctl', 'set', '10%-')),
    'lock screen': Action('Lock screen', ('xflock4',), True),
    'restart computer': Action('Restart computer', ('systemctl', 'reboot'), True),
    'shut down computer': Action('Shut down computer', ('systemctl', 'poweroff'), True),
}

REPORTS = ('system status', 'cpu status', 'memory status', 'battery status')


def normalize(text):
    normalized = ' '.join(text.lower().replace('j.a.r.v.i.s.', 'jarvis').strip().rstrip('.!?').split())
    return re.sub(r'^(?:hey )?jarvis[, ]+', '', normalized)


def parse_command(text):
    return COMMANDS.get(normalize(text))


def report_name(text):
    name = normalize(text)
    return name if name in REPORTS else None


def execute(action, approved=False):
    if action not in COMMANDS.values():
        raise ValueError('Unsupported action')
    if action.confirm and not approved:
        raise PermissionError('On-screen confirmation is required')
    if not shutil.which(action.argv[0]):
        raise RuntimeError(f'{action.argv[0]} is not installed')
    # No shell, eval, sudo, or command interpolation.
    return subprocess.Popen(list(action.argv), stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _meminfo():
    info = {}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, _, rest = line.partition(':')
            info[key] = int(rest.strip().split()[0])
    except (OSError, ValueError, IndexError):
        return None
    return info


def _battery_report():
    root = Path('/sys/class/power_supply')
    try:
        supplies = [path for path in root.iterdir() if path.name.lower().startswith(('bat', 'battery'))]
    except OSError:
        supplies = []
    for supply in supplies:
        try:
            capacity = (supply / 'capacity').read_text().strip()
            status = (supply / 'status').read_text().strip().lower()
            int(capacity)
        except (OSError, ValueError):
            continue
        return f'Battery is {capacity} percent and {status}.'
    return 'Battery information is unavailable.'


def system_report(name):
    if name not in REPORTS:
        raise ValueError('Unsupported report')
    parts = []
    if name in {'system status', 'cpu status'}:
        try:
            load = Path('/proc/loadavg').read_text().split()[0]
            parts.append(f'CPU load average is {load}.')
        except (OSError, IndexError):
            parts.append('CPU information is unavailable.')
    if name in {'system status', 'memory status'}:
        info = _meminfo()
        if info and 'MemTotal' in info and 'MemAvailable' in info:
            total = info['MemTotal'] / 1024
            used = max(0, total - (info['MemAvailable'] / 1024))
            parts.append(f'Memory used is {used:.0f} MB of {total:.0f} MB.')
        else:
            parts.append('Memory information is unavailable.')
    if name in {'system status', 'battery status'}:
        parts.append(_battery_report())
    return ' '.join(parts)


def extract_response(data):
    parts = []
    for item in data.get('output', []):
        if item.get('type') == 'message':
            for part in item.get('content', []):
                if part.get('type') == 'output_text':
                    parts.append(part.get('text', ''))
                elif part.get('type') == 'refusal':
                    parts.append(part.get('refusal', ''))
    if not parts:
        raise RuntimeError('The AI returned no text. Check the selected model and token limit.')
    return '\n'.join(parts)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Unexpected redirect from API; request stopped')


def ask_ai(text, key, model):
    if not key.strip() or not model.strip():
        raise ValueError('Enter an API key and an available model in AI Connection first.')
    if len(text) > 8000:
        raise ValueError('Please shorten the message to 8,000 characters.')
    payload = {
        'model': model.strip(), 'store': False, 'max_output_tokens': 1500,
        'instructions': (
            'You are J.A.R.V.I.S., a calm, direct and helpful desktop companion. Use clear English. '
            'You are a software assistant, not a movie character or a person. '
            'You cannot see or control this PC through this chat. Never claim you ran commands, '
            'read files, or changed settings. Local controls are separate and explicitly selected. '
            'Keep spoken replies concise.'),
        'input': text,
    }
    request = urllib.request.Request('https://api.openai.com/v1/responses',
        data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + key.strip(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=45) as response:
            return extract_response(json.load(response))
    except urllib.error.HTTPError as exc:
        reasons = {401: 'API key rejected', 403: 'Access denied', 404: 'Model unavailable',
                   429: 'API rate limit or billing quota reached'}
        raise RuntimeError(reasons.get(exc.code, f'API request failed (HTTP {exc.code})')) from None
    except urllib.error.URLError:
        raise RuntimeError('Cannot reach the AI service. Check your internet connection.') from None


def windows_command(path):
    target = Path(path).expanduser().resolve(strict=True)
    if not target.is_file() or target.suffix.lower() not in {'.exe', '.msi'}:
        raise ValueError('Choose an existing .exe or .msi file')
    if target.suffix.lower() == '.msi':
        return ['wine', 'msiexec', '/i', str(target)]
    return ['wine', str(target)]
