"""Explicit release self-test, never runs during normal launch."""
import json,sys,hashlib
from pathlib import Path
from PyQt5 import QtCore,QtGui,QtWidgets,QtTest
from .storage import resource_path

def run(app):
    from .app import DeskPet
    from .state import PetState
    report=Path(sys.argv[sys.argv.index('--self-test')+1]).resolve()
    report.parent.mkdir(parents=True,exist_ok=True)
    checks=[]
    def execute():
        try:
            pet=app.pet=DeskPet(data_dir=report.parent/'test-user-data');pet.show();app.processEvents()
            assert not app.windowIcon().isNull() and not pet.windowIcon().isNull()
            checks.append('application and window icons configured')
            for path in resource_path('assets').glob('*.gif'):
                reader=QtGui.QImageReader(str(path));assert not reader.read().isNull(),path.name
            assert len(list(resource_path('assets').glob('*.gif')))==27
            checks.append('27 GIFs decode; resource directory resolved')
            pet.set_scale_factor(.75);pet.save_position();assert pet.store.load()['scale']==.75
            checks.append('settings writable and reloadable')
            QtTest.QTest.mousePress(pet,QtCore.Qt.LeftButton,pos=QtCore.QPoint(20,20))
            event=QtGui.QMouseEvent(QtCore.QEvent.MouseMove,QtCore.QPointF(60,60),QtCore.QPointF(pet.mapToGlobal(QtCore.QPoint(60,60))),QtCore.Qt.NoButton,QtCore.Qt.LeftButton,QtCore.Qt.NoModifier)
            pet.mouseMoveEvent(event);assert pet.dragging
            QtTest.QTest.mouseRelease(pet,QtCore.Qt.LeftButton,pos=QtCore.QPoint(60,60));assert pet.state==PetState.IDLE
            pet.enter_eat_mode();pet.exit_eat_mode();pet.hide();pet.reveal()
            checks.append('drag/release, mode switch, hide/reveal')
            old=pet.gif;pet.loadGif('nonexistent.gif');assert pet.gif is old
            pet.open_gallery();app.processEvents();assert pet._settings_dialog.gallery.cards.count()==27
            nav=pet._settings_dialog.navigation
            assert nav.item(5).text()=='关于和作者'
            nav.setCurrentRow(5);app.processEvents()
            labels=pet._settings_dialog.findChildren(QtWidgets.QLabel)
            assert any('4963293161' in label.text() for label in labels)
            checks.append('about and author page, contact details')
            pet._settings_dialog.close()
            checks.append('missing resource fallback; settings and gallery')
            from PyQt5.QtMultimedia import QMediaPlayer
            from pynput import keyboard
            assert keyboard.Listener
            checks.append('audio and Windows keyboard modules import')
            report.write_text(json.dumps({'passed':True,'frozen':bool(getattr(sys,'frozen',False)),'checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
            pet.close()
        except Exception:
            import traceback
            report.write_text(json.dumps({'passed':False,'checks':checks,'error':traceback.format_exc()},ensure_ascii=False,indent=2),encoding='utf-8')
            app.exit(1)
    QtCore.QTimer.singleShot(100,execute)
    sys.exit(app.exec_())
