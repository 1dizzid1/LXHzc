import sys
from pathlib import Path
import os
SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))
os.chdir(SOURCE_ROOT)
import os,tempfile
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
from PyQt5 import QtWidgets,QtCore
from deskpet.app import DeskPet
from deskpet.storage import logger
from dialog_theme import DialogTheme
app=QtWidgets.QApplication([]);theme=DialogTheme(app);app.installEventFilter(theme)
with tempfile.TemporaryDirectory(dir='.') as folder:
 pet=DeskPet(data_dir=folder);pet.show();pet.open_gallery();app.processEvents()
 gallery=pet._settings_dialog.gallery;assert gallery.cards.count()>=27
 assert pet._settings_dialog.navigation.currentRow()==3
 assert not gallery.isWindow()
 before=dict(pet.settings)
 gallery.role.setCurrentIndex(1);gallery.cards.setCurrentRow(0)
 assert pet.settings==before
 selected=gallery.selected;gallery.confirm()
 assert pet.store.load()['action_gifs']['lift']==selected
 pet.startLift();assert Path(pet.gif.fileName()).resolve()==Path(selected).resolve()
 pet._settings_dialog.close();assert gallery.movie is None
 pet.close()
 for handler in logger.handlers[:]:handler.close();logger.removeHandler(handler)
print('PASS: gallery thumbnails, preview without mutation, confirmed persistence, drag animation, preview cleanup')
app.removeEventFilter(theme)
QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
