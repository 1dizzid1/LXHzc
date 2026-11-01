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

class ViewMixin:
    def showMenu(self, position):
        menu = QtWidgets.QMenu()
        # 仅定制右键菜单外观，保留原有菜单行为与功能。
        menu.setWindowFlags(menu.windowFlags() | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.NoDropShadowWindowHint)
        menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFF8E8;
                color: #294B3C;
                border: 2px solid #789276;
                border-radius: 14px;
                padding: 8px 6px;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei';
                font-size: 10.5pt;
                font-weight: normal;
            }
            QMenu::item {
                padding: 7px 30px 7px 18px;
                margin: 2px 4px;
                border-radius: 9px;
            }
            QMenu::item:selected {
                background-color: #DCE8CC;
                color: #234D39;
            }
            QMenu::item:disabled { color: #899581; }
            QMenu::separator {
                height: 1px;
                background-color: #D9DFC7;
                margin: 6px 14px;
            }
        """)
        # 大小和待机素材统一在设置面板调整。
        if self.is_working:
            menu.addAction("退出工作模式", self.exit_work_mode)
        elif self.is_eating:
            menu.addAction("退出吃饭模式", self.exit_eat_mode)
        elif self.state in (PetState.IDLE, PetState.ANIMATION, PetState.RANDOM):
            menu.addAction("滚动", self.startWalk)
            menu.addAction("下落", self.startFall)
            menu.addAction("吃饭", lambda: self.enter_eat_mode())
            menu.addAction("查看饱食度", lambda: self.show_speech_bubble(self.hunger_text()))
            menu.addAction('跟我来', self.start_follow)

            # 播放动图子菜单
            animation_menu = QtWidgets.QMenu("播放动图", menu)
            for name, definition in ANIMATIONS.items():
                if definition.get('menu'):
                    animation_menu.addAction(definition['label'], lambda checked=False, key=name: self.play_animation(key))
            menu.addMenu(animation_menu)
            menu.addAction("工作模式", self.enter_work_mode)
            menu.addAction("添加提醒", self.createReminderInput)
            menu.addAction("倒计时", self.createCountdownInput)
            menu.addAction("正计时", self.start_stopwatch)
        elif self.currentAction == self.startWalk:
            menu.addAction("停止", self.startIdle)
        elif self.currentAction == self.startFall:
            menu.addAction("停止", self.startIdle)
        # 子菜单使用相同的圆角透明窗口和主题。
        if self.state == PetState.FOLLOW:
            menu.addAction('停止跟随', self.startIdle)
        menu.addSeparator()
        menu.addAction('设置', self.open_settings)
        menu.addAction('动作图鉴', self.open_gallery)
        menu.addAction('提醒列表', self.manage_reminders)
        menu.addAction('隐藏', self.minimizeWindow)
        menu.addAction('退出', self.close)
        for submenu in menu.findChildren(QtWidgets.QMenu):
            submenu.setWindowFlags(submenu.windowFlags() | QtCore.Qt.FramelessWindowHint
                                   | QtCore.Qt.NoDropShadowWindowHint)
            submenu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            submenu.setStyleSheet(menu.styleSheet())
        # 用细分隔线区分互动、陪伴工具和窗口操作。
        for action in menu.actions():
            if action.text() in ("工作模式", "隐藏"):
                menu.insertSeparator(action)
        try:
            menu.exec_(self.mapToGlobal(position))
        finally:
            menu.deleteLater()


    def show_speech_bubble(self, text):
        try:
            # 如果气泡不存在则创建
            if not hasattr(self, 'speech_bubble') or not self.speech_bubble:
                # 创建气泡对象
                self.speech_bubble = QtWidgets.QDialog(self)
                
                # 设置窗口属性
                self.speech_bubble.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint |
                    QtCore.Qt.WindowStaysOnTopHint |
                    QtCore.Qt.Tool
                )
                self.speech_bubble.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                self.speech_bubble.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

                # 创建布局和标签
                self.bubble_layout = QtWidgets.QVBoxLayout(self.speech_bubble)
                self.bubble_label = QtWidgets.QLabel(self.speech_bubble)
                font_size = int(30 * self.scale_factor)
                padding = int(15 * self.scale_factor)
                radius = int(15 * self.scale_factor)
                self.bubble_label.setStyleSheet(f"""
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 1px solid #ccc;
                    border-radius: {radius}px;
                    padding: {padding}px;
                    font-size: {font_size}px;
                    color: #333;
                """)
                self.bubble_layout.addWidget(self.bubble_label)
                self.bubble_layout.setContentsMargins(0, 0, 0, 0)
                
                # 调整大小并显示
                self.speech_bubble.adjustSize()
                self.update_bubble_position()
                self.speech_bubble.show()
            
            # 更新气泡内容
            self.bubble_label.setText(text)
            self.speech_bubble.adjustSize()
            self.update_bubble_position()
            
            # 记录性能日志
            if hasattr(self, 'key_press_count') and self.key_press_count % 500 == 0:
                logger.info(f"气泡更新次数: {self.key_press_count}")
                
        except Exception as e:
            logger.error(f"更新气泡显示失败: {str(e)}")


    def update_bubble_position(self):
        """更新气泡位置使其跟随桌宠"""
        if hasattr(self, 'speech_bubble') and self.speech_bubble:
            screen_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
            # 考虑缩放比例调整位置
            offset = int(10 * self.scale_factor)
            bubble_x = screen_pos.x() + (self.width() - self.speech_bubble.width()) // 2
            bubble_y = screen_pos.y() - self.speech_bubble.height() - offset
            self.speech_bubble.move(bubble_x, bubble_y)


    def _bubble_close(self):
        bubble = getattr(self, 'speech_bubble', None)
        if bubble:
            bubble.close()
            bubble.deleteLater()
            del self.speech_bubble


    def minimizeWindow(self):
        self.showMinimized()

