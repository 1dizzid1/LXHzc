import sys
from pathlib import Path
import os
SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))
os.chdir(SOURCE_ROOT)
import os,tempfile
os.environ['QT_QPA_PLATFORM']='offscreen'
from unittest.mock import patch
from PyQt5 import QtWidgets
from deskpet.app import DeskPet
from deskpet.state import PetState
from deskpet.storage import logger
app=QtWidgets.QApplication([])
with tempfile.TemporaryDirectory(dir='.',ignore_cleanup_errors=True) as folder:
 p=DeskPet(data_dir=folder);p.show()
 with patch('deskpet.activity.random.choices',return_value=['walk']):p.choose_activity()
 assert p.state==PetState.WALK and p.activity_end.isActive()
 p.enter_eat_mode();assert not p.activity_end.isActive()
 p.start_follow();assert p.state==PetState.EAT
 p.startIdle();p.start_follow();assert p.state==PetState.FOLLOW and p.follow_timer.isActive()
 with patch('deskpet.activity.QtGui.QCursor.pos',return_value=p.geometry().center()):
  p.follow_cursor()
  position=p.pos();movie=p.gif
  assert p._follow_direction in ('run_left','run_right')
  assert 'run' in movie.fileName()
  for _ in range(5):p.follow_cursor()
  assert p.pos()==position and p.gif is movie and p.state==PetState.FOLLOW
 p.follow_end.timeout.emit();assert p.state==PetState.IDLE and not p.follow_timer.isActive()
 p.hunger_points=10
 with patch('deskpet.activity.random.choices',return_value=['walk']):p.choose_activity()
 assert p.state==PetState.IDLE
 p.generate_collectible();p.generate_collectible();assert len(p.collectibles)==1
 p._press_pos=p.pos();p.check_collectibles();assert p.state==PetState.IDLE
 del p._press_pos
 p.enter_eat_mode();assert not p.collectibles
 p.hunger_points=99;p.increase_hunger();assert p.hunger_points==100
 p.startIdle();p.set_option('quiet',True)
 with patch('deskpet.activity.random.choices',return_value=['walk']):p.choose_activity()
 assert p.state==PetState.IDLE
 p.close();assert not p.activity_timer.isActive()
 for h in logger.handlers[:]:h.close();logger.removeHandler(h)
print('PASS D: weighted activity, interruptions, following timeout, low fullness, collectible limit, drag guard, quiet mode, cleanup')
