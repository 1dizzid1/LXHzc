"""Autonomous companionship and bounded cursor following."""
import random
import math
from PyQt5 import QtCore,QtGui,QtWidgets
from .state import PetState

class ActivityMixin:
    def init_experience(self):
        super().init_experience()
        self.activity_timer=QtCore.QTimer(self);self.activity_timer.setSingleShot(True)
        self.activity_timer.timeout.connect(self.choose_activity)
        self.activity_end=QtCore.QTimer(self);self.activity_end.setSingleShot(True);self.activity_end.timeout.connect(self.startIdle)
        self.follow_timer=QtCore.QTimer(self);self.follow_timer.timeout.connect(self.follow_cursor)
        self.follow_end=QtCore.QTimer(self);self.follow_end.setSingleShot(True);self.follow_end.timeout.connect(self.startIdle)
        self.schedule_activity()

    def autonomous_allowed(self):
        return (not self._closing and self.isVisible() and not self.isMinimized() and not self.settings.get('quiet',False)
                and not self.settings.get('paused',False) and not self.is_working and not self.is_eating
                and not self.dragging and not hasattr(self,'_press_pos'))

    def schedule_activity(self):
        if hasattr(self,'activity_timer') and not self._closing:
            level=max(1,min(3,round(self.settings.get('activity_level',2))))
            self.activity_timer.start(random.randint(20,45)*1000*(4-level))

    def stopOtherActions(self):
        for name in ('activity_end','follow_timer','follow_end'):
            timer=getattr(self,name,None)
            if timer:timer.stop()
        super().stopOtherActions()

    def choose_activity(self):
        self.schedule_activity()
        if not self.autonomous_allowed() or self.state!=PetState.IDLE:return
        fullness=self.hunger_points
        weights=(8,1,1) if fullness<40 else (4,4,2)
        choice=random.choices(('rest','walk','play'),weights=weights)[0]
        if fullness<15:choice='rest'
        if choice=='walk':
            self.startWalk();self.activity_end.start(random.randint(5,14)*1000)
        elif choice=='play':
            self.play_animation(random.choice(['happy','play','tail']))
            self.activity_end.start(random.randint(6,18)*1000)

    def start_follow(self):
        if self.is_working or self.is_eating:return
        self._transition(PetState.FOLLOW)
        self._follow_direction=None
        self.follow_timer.start(40);self.follow_end.start(120000)
        self.show_speech_bubble('跟着你走，右键可随时停止。')

    def follow_cursor(self):
        if self._closing or self.dragging or not self.isVisible() or self.isMinimized():
            self.startIdle();return
        point=QtGui.QCursor.pos();screen=QtWidgets.QApplication.screenAt(point)
        if screen is None:return
        area=screen.availableGeometry()
        target=QtCore.QPoint(max(area.left(),min(point.x()-self.width()//2,area.right()+1-self.width())),max(area.top(),min(point.y()-self.height()//2,area.bottom()+1-self.height())))
        dx,dy=target.x()-self.x(),target.y()-self.y();distance=math.hypot(dx,dy)
        # Inside the following radius, keep running in place in the last direction.
        direction=(self._follow_direction or ('run_left' if dx<0 else 'run_right')) if distance<=70 else ('run_left' if dx<0 else 'run_right')
        if direction!=self._follow_direction:
            self._follow_direction=direction
            from .config import ANIMATIONS
            self.loadGif(self._asset(ANIMATIONS[direction]['file']))
        if distance<=70:return
        step=min(9,distance-70)
        self.move(round(self.x()+dx/distance*step),round(self.y()+dy/distance*step))

    def generate_collectible(self):
        if not self.autonomous_allowed() or self.state!=PetState.IDLE:return
        super().generate_collectible()

    def check_collectibles(self):
        if self.state!=PetState.IDLE or not self.autonomous_allowed():return
        # Relocate surviving collectibles if their monitor was disconnected.
        for item in self.collectibles:
            if not any(screen.availableGeometry().contains(item.geometry()) for screen in QtWidgets.QApplication.screens()):
                area=self.screen().availableGeometry();item.move(area.left(),area.top())
        super().check_collectibles()

    def moveTowardsCollectible(self):
        item=self.collectible
        if item and not any(screen.availableGeometry().contains(item.geometry()) for screen in QtWidgets.QApplication.screens()):
            area=self.screen().availableGeometry()
            item.move(area.left(),area.top())
        super().moveTowardsCollectible()

    def increase_hunger(self):
        previous=self.hunger_points
        super().increase_hunger()
        if previous<100 and self.hunger_points==100:self.show_speech_bubble('吃饱啦！现在不饿：100',priority=2)

    def update_hunger(self):
        self.hunger_points=max(0,self.hunger_points-1)
        if self.hunger_points in (39,14,0):self.show_speech_bubble(self.hunger_text(),priority=2)
