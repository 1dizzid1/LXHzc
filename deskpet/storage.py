import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import shutil
import sys
import uuid
from datetime import datetime

logger = logging.getLogger('deskpet')

def resource_path(relative):
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent)) / relative

class SettingsStore:
    DEFAULTS = {'scale': 1.0, 'idle_gif': ''}

    def __init__(self, directory=None):
        # Version-specific data never shares or overwrites older pet versions.
        self.directory = Path(directory or Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'LXHDeskPet' / '5.0')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'settings.json'

    def load(self):
        settings = dict(self.DEFAULTS)
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict): raise ValueError('settings must be an object')
            value = raw.get('scale')
            if type(value) in (int, float) and 0.5 <= value <= 2:
                settings['scale'] = float(value)
            path = raw.get('idle_gif')
            if isinstance(path, str) and path and Path(path).is_file():
                settings['idle_gif'] = path
            position = raw.get('position')
            if isinstance(position, list) and len(position) == 2 and all(type(v) is int for v in position):
                settings['position'] = position
            for key in ('paused', 'random_enabled', 'collectibles_enabled', 'quiet', 'muted', 'reminder_sound', 'countdown_sound'):
                if type(raw.get(key)) is bool: settings[key] = raw[key]
            for key, low, high in [('activity_level',1,3),('opacity',.2,1),('volume',0,1),('random_minutes',1,240),('collect_seconds',10,600)]:
                value=raw.get(key)
                if type(value) in (int,float) and low<=value<=high:settings[key]=value
            records = raw.get('reminders', [])
            mapping=raw.get('action_gifs',{})
            if isinstance(mapping,dict):
                settings['action_gifs']={key:value for key,value in mapping.items() if key in ('lift','fall','work') and isinstance(value,str) and Path(value).is_file()}
            if raw.get('sound_choice') in ('default','meow','custom'):
                settings['sound_choice']=raw['sound_choice']
            if isinstance(raw.get('custom_sound'),str):
                settings['custom_sound']=raw['custom_sound']
            settings['reminders'] = []
            if isinstance(records, list):
                for record in records:
                    try:
                        due = datetime.fromisoformat(record['due'])
                        if due.tzinfo is None and isinstance(record['text'], str):
                            settings['reminders'].append({'due': due.isoformat(), 'text': record['text']})
                    except (ValueError, TypeError, KeyError):
                        continue
        except FileNotFoundError:
            pass
        except (ValueError, OSError):
            logger.warning('Invalid settings; using defaults', exc_info=True)
            try:
                if self.path.exists(): shutil.copy2(self.path, self.directory/'settings.invalid.json')
            except OSError:
                logger.warning('Could not preserve invalid settings')
        return settings

    def save(self, settings):
        temporary = self.path.with_suffix('.tmp')
        try:
            temporary.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding='utf-8')
            os.replace(temporary, self.path)
        except OSError:
            logger.exception('Could not save settings')

    def import_animation(self, source):
        folder = self.directory / 'animations'
        folder.mkdir(exist_ok=True)
        target = folder / (uuid.uuid4().hex + '.gif')
        shutil.copy2(source, target)
        return target

    def configure_logging(self):
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(self.directory/'deskpet.log', maxBytes=1024*1024, backupCount=3, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)
