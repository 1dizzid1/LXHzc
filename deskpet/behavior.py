import os
import sys
import math
import random
import time
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from .config import ANIMATIONS, PARAMS
from .storage import resource_path, logger
from .state import PetState

def res_path(path):
    return str(resource_path(path))

class BehaviorMixin:
    def generate_collectible(self):
        if self.is_working or self.is_eating or self.dragging or self.collectibles:
            return
        area = self.screen().availableGeometry()
        size = min(int(130 * self.scale_factor), area.width(), area.height())
        item = QtWidgets.QLabel()
        movie = QtGui.QMovie(self._asset(ANIMATIONS['collectible']['file']), parent=item)
        if not movie.isValid():
            item.deleteLater()
            return
        item.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.NoDropShadowWindowHint)
        item.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        item.setFixedSize(size, size)
        movie.setScaledSize(QtCore.QSize(size, size))
        item.setMovie(movie)
        item.movie_ref = movie
        item.move(random.randint(area.left(), area.right()+1-size), random.randint(area.top(), area.bottom()+1-size))
        movie.start()
        item.show()
        self.collectibles.append(item)


    def startIdle(self):
        self.currentAction = self.startIdle
        self.moveSpeed = self.movingDirection = 0
        self.loadGif(self.idle_gif_path)


    def startWalk(self):
        self.currentAction = self.startWalk
        self.movingDirection = random.choice((-1, 1))
        self.moveSpeed = PARAMS['walk_speed']
        self._walk_image()
        self.timer.start(PARAMS['walk_tick'])
        self.changeDirectionTimer.start(PARAMS['direction_interval'])


    def startLift(self):
        self.currentAction = self.startLift
        self.loadGif(self.action_path('lift'))


    def startFall(self):
        self.currentAction = self.startFall
        self.moveSpeed = PARAMS['fall_speed']
        self.loadGif(self.action_path('fall'))
        self.timer.start(PARAMS['fall_tick'])


    def startCollect(self, collectible):
        """开始拾取物品"""
        try:
            if not collectible or not collectible.isVisible():
                logger.warning("无效的收集物对象")
                self.startIdle()
                return

            self.currentAction = self.startCollect
            self.moveSpeed = PARAMS['collect_speed']
            self.collectible = collectible
            self.timer.start(PARAMS['collect_tick'])  # 加快更新频率
            
            # 根据初始方向加载动画
            pet_rect = self.geometry()
            collectible_rect = collectible.geometry()
            dx = collectible_rect.x() - pet_rect.x()
            self.current_run_direction = 'left' if dx < 0 else 'right'
            
            logger.info(f"开始拾取物品，方向: {self.current_run_direction}")
            
            # 验证动画资源路径
            left_gif = res_path(os.path.join("assets",ANIMATIONS['run_left']['file']))
            right_gif = res_path(os.path.join("assets",ANIMATIONS['run_right']['file']))
            logger.info(f"左跑动画路径: {left_gif}")
            logger.info(f"右跑动画路径: {right_gif}")
            
            if dx < 0:
                if not os.path.exists(left_gif):
                    raise FileNotFoundError(f"左跑动画不存在: {left_gif}")
                self.loadGif(left_gif)
            else:
                if not os.path.exists(right_gif):
                    raise FileNotFoundError(f"右跑动画不存在: {right_gif}")
                self.loadGif(right_gif)
                
        except Exception as e:
            logger.error(f"开始拾取失败: {str(e)}", exc_info=True)
            self.startIdle()


    def play_eat_animation(self):
        """兼容旧方法，直接进入吃饭模式"""
        self.enter_eat_mode()


    def stopOtherActions(self):
        self.timer.stop()
        self.changeDirectionTimer.stop()
        if self._random_end:
            self._random_end.stop()
        if self._eating_timer:
            self._eating_timer.stop()
        self._session += 1
        if self.listener:
            listener, self.listener = self.listener, None
            try:
                listener.stop()
                listener.join(timeout=0.5)
            except Exception as exc:
                logger.warning('Keyboard listener cleanup: %s', exc)
        self.collectible = None
        self._bubble_close()


    def updateAnimation(self):
        if self.currentAction == self.startFall:
            self.fallPet()
        elif self.currentAction == self.startCollect:
            self.moveTowardsCollectible()
        else:
            self.movePet()


    def fallPet(self):
        floor = self.screen().availableGeometry().bottom() + 1 - self.height()
        self.move(self.x(), min(self.y() + self.moveSpeed, floor))
        if self.y() >= floor:
            self.startIdle()


    def movePet(self):
        if self.currentAction != self.startWalk or self.dragging:
            return
        area = self.screen().availableGeometry()
        x = self.x() + self.moveSpeed * self.movingDirection
        low, high = area.left(), max(area.left(), area.right() + 1 - self.width())
        if x < low or x > high:
            x = max(low, min(high, x))
            self.changeDirection()
        self.move(x, self.y())


    def moveTowardsCollectible(self):
        item = self.collectible
        if not item:
            self.startIdle()
            return
        if self.geometry().intersects(item.geometry()):
            self.collectibles.remove(item)
            item.close()
            item.deleteLater()
            self.startIdle()
            return
        delta = item.geometry().center() - self.geometry().center()
        distance = math.hypot(delta.x(), delta.y())
        step = min(self.moveSpeed, distance)
        self.move(self.x()+round(delta.x()*step/distance), self.y()+round(delta.y()*step/distance))
        direction = 'left' if delta.x() < 0 else 'right'
        if direction != self.current_run_direction:
            self.current_run_direction = direction
            self.loadGif(self._asset(ANIMATIONS['run_left']['file'] if direction == 'left' else ANIMATIONS['run_right']['file']))


    def enter_work_mode(self):
        self.currentAction = self.enter_work_mode
        self.key_press_count = 0
        self.loadGif(self.action_path('work'))
        self.show_speech_bubble('工作模式\n按键次数：0')
        session = self._session
        held = set()
        def identity(key):
            return getattr(key, 'vk', None) or getattr(getattr(key, 'value', None), 'vk', None) or str(key)
        def press(key):
            token = identity(key)
            if token not in held:
                held.add(token)
                self._bridge.pressed.emit(session)
        def release(key):
            held.discard(identity(key))
        try:
            from pynput import keyboard
            self.listener = keyboard.Listener(on_press=press, on_release=release)
            self.listener.start()
        except Exception as exc:
            self.startIdle()
            self.show_speech_bubble('键盘监听启动失败：' + str(exc))


    def keyPressEvent(self, event):
        """窗口内键盘按键事件处理"""
        pass  # 现在由全局快捷键处理按键计数


    def exit_work_mode(self):
        self.startIdle()


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._press_pos = event.globalPos()
            self.drag_position = event.globalPos() - self.pos()
            self.dragging = False
            self.timer.stop()
            self.changeDirectionTimer.stop()
            event.accept()


    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton and hasattr(self, '_press_pos'):
            if not self.dragging and (event.globalPos()-self._press_pos).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
                self.dragging = True
                if not self.is_working and not self.is_eating:
                    self.startLift()
            if self.dragging:
                self.move(event.globalPos()-self.drag_position)
                self.update_bubble_position()
            event.accept()


    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            if hasattr(self, '_press_pos'):
                del self._press_pos
            if not self.is_working and not self.is_eating:
                self.startIdle()
            event.accept()


    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)


    def check_collectibles(self):
        if not hasattr(self, '_press_pos') and not self.dragging and not self.is_working and not self.is_eating and not self.is_playing_random_animation and self.state == PetState.IDLE:
            if self.collectibles:
                self.startCollect(self.collectibles[0])


    def enter_eat_mode(self):
        self.currentAction = self.enter_eat_mode
        self.loadGif(self.action_path('eat'))
        self._eating_timer.start(PARAMS['eat_interval'])
        self.show_speech_bubble(self.hunger_text())


    def exit_eat_mode(self):
        self.startIdle()


    def increase_hunger(self):
        """每秒增加1点饥饿值"""
        self.hunger_points = min(100, self.hunger_points + 1)
        self.show_speech_bubble(self.hunger_text())


    def stop_eat_animation(self):
        self.startIdle()


    def update_hunger(self):
        """每2分钟减少1点饥饿值"""
        self.hunger_points = max(0, self.hunger_points - 1)
        if self.hunger_points <= 20:
            self.show_speech_bubble(self.hunger_text())


    def play_random_animation(self):
        if hasattr(self, '_press_pos') or self.dragging or self.state != PetState.IDLE:
            return
        choices = [key for key, value in ANIMATIONS.items() if value.get('weight', 0) > 0]
        name = random.choices(choices, weights=[ANIMATIONS[key]['weight'] for key in choices])[0]
        self.currentAction = self.play_random_animation
        self.loadGif(self._asset(ANIMATIONS[name]['file']))
        self._random_end.start(PARAMS['random_duration'])

    def end_random_animation(self):
        if self.is_playing_random_animation and not self._closing:
            self.startIdle()


    def changeDirection(self):
        if self.currentAction == self.startWalk:
            self.movingDirection *= -1
            self._walk_image()


    def closeEvent(self, event):
        self._closing = True
        self.stopOtherActions()
        for timer in self.findChildren(QtCore.QTimer):
            timer.stop()
        if self.gif:
            self.gif.stop()
            self.setMovie(None)
            self.gif.deleteLater()
            self.gif = None
        for item in self.collectibles:
            item.close()
            item.deleteLater()
        self.collectibles.clear()
        for dialog in self.findChildren(QtWidgets.QDialog):
            dialog.close()
        event.accept()
        QtWidgets.QApplication.instance().quit()


    def hunger_text(self):
        value = self.hunger_points
        if value >= 80:
            description = '现在不饿'
        elif value >= 60:
            description = '有点嘴馋'
        elif value >= 40:
            description = '肚子饿了'
        elif value >= 15:
            description = '好饿啊！'
        else:
            description = '饿晕了'
        return f'{description}：{value}'


    def _resume_background(self):
        if self._closing:
            return
        self.collectible_timer.start(PARAMS['collect_interval'])
        self.collectible_check_timer.start(PARAMS['collect_check'])
        if hasattr(self, 'random_animation_timer'):
            self.random_animation_timer.start(PARAMS['random_interval'])


    def _walk_image(self):
        self.loadGif(self._asset(ANIMATIONS['walk_left']['file'] if self.movingDirection < 0 else ANIMATIONS['walk_right']['file']))


    def _count_key(self, session):
        if self.is_working and not self._closing and session == self._session:
            self.key_press_count += 1
            self.show_speech_bubble(f'工作模式\n按键次数：{self.key_press_count}')


    def play_animation(self, name):
        self._transition(PetState.ANIMATION)
        self.loadGif(self._asset(ANIMATIONS[name]['file']))
