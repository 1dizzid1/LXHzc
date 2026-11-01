import sys
from pathlib import Path
import os
SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))
os.chdir(SOURCE_ROOT)
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import importlib.util
import sys
import types
from unittest.mock import patch
from PyQt5 import QtWidgets, QtCore
spec = importlib.util.spec_from_file_location('pet_app', '罗小黑桌宠.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = QtWidgets.QApplication([])
import tempfile
from pathlib import Path
data = tempfile.TemporaryDirectory(dir='.', ignore_cleanup_errors=True)
pet = module.DeskPet(data_dir=data.name)
pet.show()
assert pet.hunger_timer.isActive() and pet.collectible_timer.isActive()
pet.update_hunger()
assert pet.hunger_points == 99
old = pet.gif
pet.loadGif('missing.gif')
assert pet.gif is old
pet.play_random_animation()
assert pet._random_end.isActive()
pet.enter_eat_mode()
assert not pet._random_end.isActive() and pet.is_eating
pet.end_random_animation()
assert pet.is_eating
pet.exit_eat_mode()
assert not pet.is_eating and pet.collectible_timer.isActive()
class Listener:
    def __init__(self, **callbacks): self.callbacks = callbacks
    def start(self): pass
    def stop(self): pass
    def join(self, timeout): pass
fake = types.SimpleNamespace(keyboard=types.SimpleNamespace(Listener=Listener))
with patch.dict(sys.modules, {'pynput': fake}):
    pet.enter_work_mode()
    callbacks = pet.listener.callbacks
    key = types.SimpleNamespace(vk=65)
    for _ in range(10): callbacks['on_press'](key)
    app.processEvents()
    assert pet.key_press_count == 1
    callbacks['on_release'](key)
    callbacks['on_press'](key)
    app.processEvents()
    assert pet.key_press_count == 2
    old_session = pet._session
    pet.exit_work_mode()
    pet._count_key(old_session)
    assert pet.key_press_count == 2 and pet.listener is None
pet.start_stopwatch()
window = pet.stopwatch_window
pet.start_stopwatch()
assert pet.stopwatch_window is window
with patch('deskpet.clocks.time.monotonic', return_value=100): pet._start_stopwatch_timer()
with patch('deskpet.clocks.time.monotonic', return_value=165.9): pet.update_stopwatch()
assert pet.stopwatch_label.text() == '00:01:05'
with patch('deskpet.clocks.time.monotonic', return_value=166): pet.pause_stopwatch()
assert pet._elapsed == 66
pet.stop_stopwatch()
assert not pet.stopwatch_timer.isActive() and pet.stopwatch_window is None
pet.createCountdownInput()
pet.second_spinbox.setValue(10)
with patch('deskpet.clocks.time.monotonic', return_value=100): pet.start_countdown()
with patch('deskpet.clocks.time.monotonic', return_value=104.2): pet.update_countdown()
assert pet.countdown_time == 6
pet.countdown_window.close()
assert not pet.countdown_timer.isActive() and pet.countdown_time is None
pet.generate_collectible()
assert len(pet.collectibles) == 1
pet.startCollect(pet.collectibles[0])
pet.startIdle()
pet.startWalk()
before = pet.movingDirection
pet.changeDirection()
assert pet.movingDirection == -before
pet.close()
assert all(not t.isActive() for t in pet.findChildren(QtCore.QTimer))
print('PASS: assets, timers, mode cancellation, held keys, stale events, clocks, window reuse, cleanup')
import logging
logging.shutdown()
data.cleanup()
