"""Validated, atomic JSON preferences; never restore power automatically."""
import json
import os
from pathlib import Path

def data_dir():
    return Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'LightControl'

def defaults():
    return dict(host='10.10.123.3', port=5577, rgb=[255, 150, 60],
                brightness=100, white=100, mode='RGB', auto=False, preset=0)

def load(path=None):
    path = path or data_dir() / 'settings.json'
    result = defaults()
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(raw, dict):
            return result
        for key in result:
            value = raw.get(key)
            if key == 'host' and isinstance(value, str) and value.strip():
                result[key] = value.strip()
            elif key == 'rgb' and isinstance(value, list) and len(value) == 3 and all(type(x) is int and 0 <= x <= 255 for x in value):
                result[key] = value
            elif key in ('port', 'brightness', 'white', 'preset') and type(value) is int:
                limit = {'port': (1, 65535), 'brightness': (0, 100), 'white': (0, 100), 'preset': (0, 3)}[key]
                if limit[0] <= value <= limit[1]:
                    result[key] = value
            elif key == 'mode' and value in ('RGB', 'Blanco cálido'):
                result[key] = value
            elif key == 'auto' and type(value) is bool:
                result[key] = value
    except (OSError, ValueError):
        pass
    return result

def save(values, path=None):
    path = path or data_dir() / 'settings.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(values, indent=2), encoding='utf-8')
    temporary.replace(path)
