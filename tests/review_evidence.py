"""Review actual rendered output; never infer GUI success from a green capture job."""
import json
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageOps, ImageChops, ImageStat

root = Path('evidence')
report = {}

def ocr(name, crop=None):
    path = root / name
    if crop:
        with Image.open(path) as image:
            part = image.crop(crop(image))
            path = root / ('crop-' + name)
            part.save(path)
    result = subprocess.run(['tesseract', str(path), 'stdout', '--psm', '11'],
                            capture_output=True, text=True, check=True)
    (root / (name + '.txt')).write_text(result.stdout)
    print('OCR ' + name + ': ' + result.stdout[:2500], flush=True)
    return re.sub('[^A-Z0-9]', '', result.stdout.upper())

with Image.open(root / 'desktop-wallpaper.png') as image:
    actual = image.convert('RGB')
    width, height = actual.size
with Image.open('expected-wallpaper.png') as image:
    expected = ImageOps.fit(image.convert('RGB'), (width, height))
box = (0, 0, width, height - 50)
difference = ImageStat.Stat(ImageChops.difference(actual.crop(box), expected.crop(box)))
report['wallpaper_mean_channel_difference'] = sum(difference.mean) / 3
report['wallpaper_matches'] = report['wallpaper_mean_channel_difference'] < 12
clock = actual.crop((width - 115, height - 38, width - 8, height - 2))
report['clock_bright_pixels'] = sum(min(pixel) > 170 for pixel in clock.getdata())
report['clock_readable_color'] = report['clock_bright_pixels'] > 100

assistant = ocr('boot-180s.png')
report['assistant_visible'] = any(word in assistant for word in [
    'YOURVOICEYOURDESKTOP', 'DESKTOPCOMPANION', 'RUNCOMMAND'])
chrome = ocr('chrome-launch.png', lambda im: (0, 0, im.width, 150))
report['chrome_toolbar_visible'] = 'CHROME' in chrome
vlc = ocr('vlc-launch.png')
report['vlc_visible'] = any(word in vlc for word in [
    'VLCMEDIAPLAYER', 'PRIVACYANDNETWORKACCESSPOLICY'])
ocr('app-menu.png')
ocr('runtime-report.png')
Path('rendered-review.json').write_text(json.dumps(report, indent=2))
print('RENDERED_REVIEW=' + json.dumps(report), flush=True)
required = ['wallpaper_matches', 'clock_readable_color', 'assistant_visible',
            'chrome_toolbar_visible', 'vlc_visible']
if not all(report[key] for key in required):
    raise SystemExit('Rendered evidence needs inspection: ' + str(report))
