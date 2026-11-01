import sys
from pathlib import Path
import os
SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))
os.chdir(SOURCE_ROOT)
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import tempfile
from unittest.mock import patch
from PyQt5 import QtWidgets,QtGui
from deskpet.app import DeskPet
from deskpet.storage import logger
app=QtWidgets.QApplication([])
with tempfile.TemporaryDirectory(dir='.') as directory:
    pet=DeskPet(data_dir=directory);pet.show()
    old=pet.gif;pet.startIdle();assert pet.gif is old
    pet.set_option('quiet',True)
    assert not pet.collectible_timer.isActive() and not pet.random_animation_timer.isActive()
    pet.show_speech_bubble('ordinary');assert not hasattr(pet,'speech_bubble')
    pet.show_speech_bubble('important',priority=3);assert pet.bubble_label.text()=='important'
    pet.set_option('muted',True);pet.notification_sound(preview=True);assert pet._sound is None
    pet.hide();assert pet.gif.state()==QtGui.QMovie.Paused
    pet.reveal();assert pet.gif.state()==QtGui.QMovie.Running
    pet.set_option('quiet',False);assert pet.collectible_timer.isActive()
    pet.open_settings();assert pet._settings_dialog.isVisible()
    pet.close()
    for handler in logger.handlers[:]:handler.close();logger.removeHandler(handler)
print('PASS: settings panel, quiet priority, mute, reuse, hidden pause/resume')
