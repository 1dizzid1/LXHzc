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

class ClocksMixin:
    def _raise_existing(self, name):
        dialog = getattr(self, name, None)
        if dialog and dialog.isVisible():
            dialog.raise_()
            dialog.activateWindow()
            return True
        return False


    def createCountdownInput(self):
        if self._raise_existing('countdown_window') or self._raise_existing('countdown_dialog'):
            return
        self.countdown_dialog = QtWidgets.QDialog(self)
        self.countdown_dialog.setWindowTitle("设置倒计时")
        self.countdown_dialog.setModal(True)
        layout = QtWidgets.QVBoxLayout(self.countdown_dialog)

        hour_layout = QtWidgets.QHBoxLayout()
        hour_label = QtWidgets.QLabel("小时:", self.countdown_dialog)
        self.hour_spinbox = QtWidgets.QSpinBox(self.countdown_dialog)
        self.hour_spinbox.setRange(0, 24)
        hour_layout.addWidget(hour_label)
        hour_layout.addWidget(self.hour_spinbox)

        minute_layout = QtWidgets.QHBoxLayout()
        minute_label = QtWidgets.QLabel("分钟:", self.countdown_dialog)
        self.minute_spinbox = QtWidgets.QSpinBox(self.countdown_dialog)
        self.minute_spinbox.setRange(0, 59)
        minute_layout.addWidget(minute_label)
        minute_layout.addWidget(self.minute_spinbox)

        second_layout = QtWidgets.QHBoxLayout()
        second_label = QtWidgets.QLabel("秒数:", self.countdown_dialog)
        self.second_spinbox = QtWidgets.QSpinBox(self.countdown_dialog)
        self.second_spinbox.setRange(0, 59)
        second_layout.addWidget(second_label)
        second_layout.addWidget(self.second_spinbox)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
                                                self.countdown_dialog)
        button_box.accepted.connect(self.start_countdown)
        button_box.rejected.connect(self.countdown_dialog.reject)

        layout.addLayout(hour_layout)
        layout.addLayout(minute_layout)
        layout.addLayout(second_layout)
        layout.addWidget(button_box)

        font = QtGui.QFont()
        font.setPointSize(12)
        self.countdown_dialog.setFont(font)

        self.countdown_dialog.show()
        self.countdown_dialog.finished.connect(self.countdown_dialog.deleteLater)
        self.countdown_dialog.finished.connect(lambda: setattr(self, 'countdown_dialog', None))


    def start_countdown(self):
        seconds = self.hour_spinbox.value()*3600 + self.minute_spinbox.value()*60 + self.second_spinbox.value()
        if seconds <= 0:
            QtWidgets.QMessageBox.warning(self, '错误', '倒计时时间必须大于0！')
            return
        self.countdown_time = seconds
        self._deadline = time.monotonic() + seconds
        self.countdown_window = QtWidgets.QDialog(self)
        self.countdown_window.setWindowTitle('倒计时')
        layout = QtWidgets.QVBoxLayout(self.countdown_window)
        self.countdown_label = QtWidgets.QLabel()
        self.countdown_label.setFont(QtGui.QFont('Microsoft YaHei UI', 20))
        layout.addWidget(self.countdown_label)
        self.countdown_window.finished.connect(self._close_countdown)
        self.update_countdown_display()
        self.countdown_window.show()
        self.countdown_timer.start(100)
        self.countdown_dialog.accept()


    def _close_countdown(self):
        self.countdown_timer.stop()
        self.countdown_time = None
        dialog, self.countdown_window = self.countdown_window, None
        if dialog:
            dialog.deleteLater()


    def update_countdown(self):
        if self.countdown_time is None:
            return
        self.countdown_time = max(0, math.ceil(self._deadline - time.monotonic()))
        self.update_countdown_display()
        if self.countdown_time == 0:
            self.countdown_window.accept()
            if not self._closing:
                self.show_countdown_finished_dialog()


    def update_countdown_display(self):
        if self.countdown_time is None:
            return

        hours = self.countdown_time // 3600
        minutes = (self.countdown_time % 3600) // 60
        seconds = self.countdown_time % 60
        self.countdown_label.setText(f"剩余时间: {hours} 小时 {minutes} 分钟 {seconds} 秒")


    def show_countdown_finished_dialog(self):
        font = QtGui.QFont()
        font.setPointSize(12)
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("倒计时完成")
        msg_box.setText("倒计时已完成！")
        msg_box.setFont(font)
        msg_box.exec_()


    def start_stopwatch(self):
        if self._raise_existing('stopwatch_window'):
            return
        self._elapsed, self._started = 0.0, None
        """启动正计时"""
        self.stopwatch_time = 0
        self.is_paused = False
        self.stopwatch_window = QtWidgets.QDialog(self)
        self.stopwatch_window.setWindowTitle("正计时")
        layout = QtWidgets.QVBoxLayout(self.stopwatch_window)
        
        self.stopwatch_label = QtWidgets.QLabel("00:00:00")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.stopwatch_label.setFont(font)
        layout.addWidget(self.stopwatch_label)
        
        button_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("开始")
        self.pause_button = QtWidgets.QPushButton("暂停")
        self.stop_button = QtWidgets.QPushButton("停止")
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        self.start_button.clicked.connect(self._start_stopwatch_timer)
        self.pause_button.clicked.connect(self.pause_stopwatch)
        self.stop_button.clicked.connect(self.stop_stopwatch)
        
        self.pause_button.setEnabled(False)
        self.stopwatch_window.show()
        self.stopwatch_window.finished.connect(self._close_stopwatch)


    def _start_stopwatch_timer(self):
        if self._started is not None:
            return
        self._started = time.monotonic()
        self.is_paused = False
        self.stopwatch_timer.start(100)
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)


    def update_stopwatch(self):
        elapsed = self._elapsed + (time.monotonic()-self._started if self._started is not None else 0)
        self.stopwatch_time = int(elapsed)
        h, remainder = divmod(self.stopwatch_time, 3600)
        m, s = divmod(remainder, 60)
        self.stopwatch_label.setText(f'{h:02d}:{m:02d}:{s:02d}')


    def pause_stopwatch(self):
        if self._started is not None:
            self._elapsed += time.monotonic()-self._started
            self._started = None
        self.is_paused = True
        self.stopwatch_timer.stop()
        self.update_stopwatch()
        self.start_button.setText('继续')
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)


    def _close_stopwatch(self):
        self.stopwatch_timer.stop()
        self._started = None
        dialog, self.stopwatch_window = self.stopwatch_window, None
        if dialog:
            dialog.deleteLater()


    def stop_stopwatch(self):
        if self.stopwatch_window:
            self.stopwatch_window.close()


    def createReminderInput(self):
        self.reminder_input = QtWidgets.QInputDialog(self)
        self.reminder_input.setInputMode(QtWidgets.QInputDialog.TextInput)
        self.reminder_input.setWindowTitle("添加提醒")
        self.reminder_input.setLabelText("请输入提醒内容:")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.reminder_input.setFont(font)
        if self.reminder_input.exec_() == QtWidgets.QDialog.Accepted:
            reminder_text = self.reminder_input.textValue()
            self.set_reminder(reminder_text)


    def set_reminder(self, reminder_text):
        time_dialog = QtWidgets.QTimeEdit(self)
        time_dialog.setWindowTitle("设置提醒时间")
        time_dialog.setCalendarPopup(True)
        font = QtGui.QFont()
        font.setPointSize(12)
        time_dialog.setFont(font)
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("设置提醒时间")
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(time_dialog)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setFont(font)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            reminder_time = time_dialog.time().toPyTime()
            current_time = datetime.now().time()
            if reminder_time < current_time:
                QtWidgets.QMessageBox.warning(self, "错误", "提醒时间不能早于当前时间！")
                return
            self.reminders.append((reminder_time, reminder_text))
            QtWidgets.QMessageBox.information(self, "成功", "提醒已设置！")


    def check_reminders(self):
        current_time = datetime.now().time()
        for reminder in list(self.reminders):
            reminder_time, reminder_text = reminder
            if current_time.hour == reminder_time.hour and current_time.minute == reminder_time.minute:
                self.reminders.remove(reminder)
                self.showReminderDialog(reminder_text)


    def showReminderDialog(self, reminder_text):
        font = QtGui.QFont()
        font.setPointSize(12)
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("提醒")
        msg_box.setText(f"提醒: {reminder_text}")
        msg_box.setFont(font)
        msg_box.exec_()

