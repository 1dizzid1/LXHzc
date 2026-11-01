import sys
from pathlib import Path
import os
SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))
os.chdir(SOURCE_ROOT)
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import ast
import json
import logging
import tempfile
from pathlib import Path
from deskpet.app import DeskPet
from deskpet.storage import SettingsStore, logger
from deskpet.state import PetState
from deskpet.config import ANIMATIONS
from PyQt5 import QtWidgets, QtCore
from dialog_theme import DialogTheme
app=QtWidgets.QApplication([])
app.theme=DialogTheme(app); app.installEventFilter(app.theme)
with tempfile.TemporaryDirectory(dir='.') as directory:
    store=SettingsStore(directory)
    store.path.write_text('{broken',encoding='utf-8')
    assert store.load()==store.DEFAULTS
    assert (Path(directory)/'settings.invalid.json').exists()
    store.save({'scale': 1.25,'idle_gif':''})
    assert store.load()['scale']==1.25
    pet=DeskPet(data_dir=directory); pet.show()
    assert pet.scale_factor==1.25
    def foot(): return pet.x()+pet.width()/2,pet.y()+pet.height()
    anchor=foot()
    pet.play_animation('fish')
    assert pet.state==PetState.ANIMATION
    assert abs(foot()[0]-anchor[0])<=0.5 and foot()[1]==anchor[1]
    pet.set_scale_factor(0.75)
    assert abs(foot()[0]-anchor[0])<=1 and foot()[1]==anchor[1]
    assert store.load()['scale']==0.75
    pet.play_random_animation()
    assert pet.state==PetState.ANIMATION
    pet.startIdle(); pet.play_random_animation()
    assert pet.state==PetState.RANDOM and pet._random_end.isActive()
    pet.play_animation('happy')
    assert pet.state==PetState.ANIMATION and not pet._random_end.isActive()
    pet.enter_eat_mode()
    assert pet.state==PetState.EAT and not pet.collectible_timer.isActive()
    pet.startWalk()
    assert pet.state==PetState.WALK and not pet._eating_timer.isActive() and pet.collectible_timer.isActive()
    imported=store.import_animation(pet._asset(ANIMATIONS['idle']['file']))
    assert imported.parent==Path(directory)/'animations'
    pet.createCountdownInput(); app.processEvents()
    assert pet.countdown_dialog.property('forestRounded')
    assert pet.countdown_dialog.windowFlags() & QtCore.Qt.WindowStaysOnTopHint
    assert not pet.countdown_dialog.testAttribute(QtCore.Qt.WA_TranslucentBackground)
    assert logger.handlers[0].maxBytes==1024*1024 and logger.handlers[0].backupCount==3
    pet.close()
    for handler in logger.handlers[:]: handler.close(); logger.removeHandler(handler)
for path in Path('deskpet').glob('*.py'):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'))
    for cls in [n for n in tree.body if isinstance(n,ast.ClassDef)]:
        names=[n.name for n in cls.body if isinstance(n,ast.FunctionDef)]
        duplicates={n for n in names if names.count(n)>1}
        assert duplicates <= {'currentAction'} # getter and setter
print('PASS B: settings recovery/persistence, resource import, anchors, states, card dialogs, log rotation, unique methods')
