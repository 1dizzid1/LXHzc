import sys
from pathlib import Path
import os
SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))
os.chdir(SOURCE_ROOT)
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from datetime import datetime, timedelta
import tempfile
from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from deskpet.app import DeskPet
from deskpet.storage import SettingsStore, logger
app=QtWidgets.QApplication([])
with tempfile.TemporaryDirectory(dir='.') as directory:
    store=SettingsStore(directory)
    store.save({'scale':1,'position':[-90000,90000],'paused':True,'random_enabled':False,
                'reminders':[{'due':(datetime.now()-timedelta(hours=1)).isoformat(),'text':'past'}]})
    pet=DeskPet(data_dir=directory); pet.show()
    assert pet.screen().availableGeometry().intersects(pet.geometry())
    assert not pet.collectible_timer.isActive() and not pet.random_animation_timer.isActive()
    pet.check_reminders()
    assert not store.load()['reminders']
    pet.check_reminders()
    pet.show_speech_bubble('important',priority=3)
    pet.show_speech_bubble('ordinary',priority=1)
    assert pet.bubble_label.text()=='important'
    assert pet.screen().availableGeometry().contains(pet.speech_bubble.geometry())
    pet._expire_bubble(); assert not hasattr(pet,'speech_bubble')
    pet.set_option('paused',False)
    assert pet.collectible_timer.isActive() and not pet.random_animation_timer.isActive()
    pet.restore_idle(); assert store.load()['idle_gif']==''
    pet.move(100,120);pet.save_position()
    assert store.load()['position']==[100,120]
    pet.close()
    for handler in logger.handlers[:]:handler.close();logger.removeHandler(handler)
print('PASS C: offscreen recovery, saved switches, overdue delivery once, priority, bubble bounds, restore idle, saved position')
