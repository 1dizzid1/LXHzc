"""Persistent desktop experience: tray, reminders, screens and notifications."""
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from .config import PARAMS, ANIMATIONS

class ExperienceMixin:
    def init_experience(self):
        self._bubble_priority = -1
        self._bubble_timeout = QtCore.QTimer(self)
        self._bubble_timeout.setSingleShot(True)
        self._bubble_timeout.timeout.connect(self._expire_bubble)
        self._position_save = QtCore.QTimer(self)
        self._position_save.setSingleShot(True)
        self._position_save.timeout.connect(self.save_position)
        position = self.settings.get('position')
        if position:
            self.move(*position)
        self.ensure_visible()
        app = QtWidgets.QApplication.instance()
        for screen in app.screens(): self._connect_screen(screen)
        app.screenAdded.connect(self._connect_screen)
        app.screenRemoved.connect(lambda screen: QtCore.QTimer.singleShot(0, self.ensure_visible))
        self.tray = QtWidgets.QSystemTrayIcon(self)
        icon = QtGui.QIcon(self._asset('lxh.ico'))
        if icon.isNull(): icon = app.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.setToolTip('罗小黑桌宠')
        menu = QtWidgets.QMenu(self)
        menu.addAction('显示小黑', self.reveal)
        menu.addAction('隐藏小黑', self.minimizeWindow)
        pause = menu.addAction('暂停自主活动')
        pause.setCheckable(True)
        pause.setChecked(self.settings.get('paused', False))
        pause.toggled.connect(lambda checked: self.set_option('paused', checked))
        self._pause_action = pause
        menu.addAction('设置', self.open_settings)
        menu.addAction('提醒列表', self.manage_reminders)
        menu.addSeparator()
        menu.addAction('退出', self.close)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.reveal() if reason == QtWidgets.QSystemTrayIcon.DoubleClick else None)
        self.tray.show()
        self._resume_background()
        QtCore.QTimer.singleShot(0, self.check_reminders)

    def _connect_screen(self, screen):
        screen.availableGeometryChanged.connect(lambda rect: self.ensure_visible())
        self.ensure_visible()

    def ensure_visible(self):
        screens = QtWidgets.QApplication.screens()
        screen = QtWidgets.QApplication.screenAt(self.geometry().center()) or QtWidgets.QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.move(max(area.left(), min(self.x(), max(area.left(), area.right()+1-self.width()))),
                  max(area.top(), min(self.y(), max(area.top(), area.bottom()+1-self.height()))))
        self.update_bubble_position()

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, '_position_save'):
            self._position_save.start(350)
            self.update_bubble_position()

    def save_position(self):
        self.settings['position'] = [self.x(), self.y()]
        self.store.save(self.settings)

    def reveal(self):
        self.ensure_visible()
        self.showNormal()
        self.raise_()

    def _resize_anchored(self, size):
        super()._resize_anchored(size)
        self.ensure_visible()

    def minimizeWindow(self):
        self._expire_bubble()
        if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable(): self.hide()
        else: self.showMinimized()

    def set_option(self, key, value):
        self.settings[key] = bool(value)
        self.store.save(self.settings)
        if key == 'paused' and value: self.startIdle()
        self._resume_background()
        if hasattr(self, '_pause_action'):
            self._pause_action.blockSignals(True)
            self._pause_action.setChecked(self.settings.get('paused', False))
            self._pause_action.blockSignals(False)

    def _resume_background(self):
        if self._closing: return
        paused = self.settings.get('paused', False) or self.is_working or self.is_eating
        for timer, enabled, interval in [
            (self.collectible_timer, self.settings.get('collectibles_enabled', True), PARAMS['collect_interval']),
            (self.collectible_check_timer, self.settings.get('collectibles_enabled', True), PARAMS['collect_check']),
            (self.random_animation_timer, self.settings.get('random_enabled', True), PARAMS['random_interval']),
        ]:
            if paused or not enabled: timer.stop()
            elif not timer.isActive(): timer.start(interval)

    def open_settings(self):
        if self._raise_existing('_settings_dialog'): return
        dialog = self._settings_dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('小黑设置')
        layout = QtWidgets.QVBoxLayout(dialog)
        for key, text, default in [('paused','暂停自主活动',False), ('random_enabled','随机动画',True), ('collectibles_enabled','嘿咻拾取',True)]:
            check = QtWidgets.QCheckBox(text)
            check.setChecked(self.settings.get(key,default))
            check.toggled.connect(lambda value, k=key: self.set_option(k,value))
            layout.addWidget(check)
        for text, callback in [('提醒列表',self.manage_reminders),('更换待机动图',self.change_idle_gif),('恢复默认待机动画',self.restore_idle)]:
            button=QtWidgets.QPushButton(text); button.clicked.connect(callback); layout.addWidget(button)
        dialog.show()

    def restore_idle(self):
        self.settings['idle_gif']=''
        self.idle_gif_path=self._asset(ANIMATIONS['idle']['file'])
        self.store.save(self.settings)
        self.startIdle()

    def set_reminder(self, reminder_text):
        if not reminder_text.strip(): return
        dialog=QtWidgets.QDialog(self); dialog.setWindowTitle('设置提醒日期与时间')
        layout=QtWidgets.QVBoxLayout(dialog)
        editor=QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime().addSecs(60),dialog)
        editor.setDisplayFormat('yyyy-MM-dd HH:mm:ss'); editor.setCalendarPopup(True)
        layout.addWidget(editor)
        buttons=QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec_()==QtWidgets.QDialog.Accepted:
            due=editor.dateTime().toPyDateTime()
            if due<=datetime.now():
                QtWidgets.QMessageBox.warning(self,'提醒','请选择未来的时间。'); return
            self.settings.setdefault('reminders',[]).append({'due':due.isoformat(),'text':reminder_text.strip()})
            self.store.save(self.settings)
        dialog.deleteLater()

    def check_reminders(self):
        records=self.settings.get('reminders',[])
        due=[r for r in records if datetime.fromisoformat(r['due'])<=datetime.now()]
        if not due:return
        self.settings['reminders']=[r for r in records if r not in due]
        self.store.save(self.settings)
        message='\n'.join(r['text'] for r in due)
        self.notification_sound('reminder')
        box=QtWidgets.QDialog(self)
        box.setWindowTitle('提醒（含离线期间到期提醒）')
        layout=QtWidgets.QVBoxLayout(box)
        text=QtWidgets.QTextBrowser(box)
        text.setPlainText(message)
        layout.addWidget(text)
        button=QtWidgets.QPushButton('知道了',box)
        button.clicked.connect(box.accept)
        layout.addWidget(button)
        box.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,True)
        box.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        box.show()
        self.show_speech_bubble(message,priority=3,duration=15000)

    def manage_reminders(self):
        dialog=QtWidgets.QDialog(self); dialog.setWindowTitle('提醒列表')
        layout=QtWidgets.QVBoxLayout(dialog); listing=QtWidgets.QListWidget(); layout.addWidget(listing)
        records=list(self.settings.get('reminders',[]))
        for record in records: listing.addItem(record['due'].replace('T',' ')+'  '+record['text'])
        layout.addWidget(QtWidgets.QLabel('错过的提醒将在下次启动时补发一次。'))
        button=QtWidgets.QPushButton('删除选中提醒'); layout.addWidget(button)
        def remove():
            index=listing.currentRow()
            if index<0:return
            record=records.pop(index); listing.takeItem(index)
            if record in self.settings.get('reminders',[]):self.settings['reminders'].remove(record)
            self.store.save(self.settings)
        button.clicked.connect(remove)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose); dialog.show()

    def _expire_bubble(self):
        self._bubble_priority=-1
        super()._bubble_close()

    def _bubble_close(self):
        if hasattr(self,'_bubble_timeout'):self._bubble_timeout.stop()
        self._bubble_priority=-1
        super()._bubble_close()

    def show_speech_bubble(self,text,priority=1,duration=5000):
        if not hasattr(self,'_bubble_timeout'):return
        if not self.isVisible():return
        if priority<self._bubble_priority:return
        self._bubble_priority=priority
        # Full reminder text remains available in its scrollable dialog.
        text = text if len(text) <= 160 else text[:160] + '…'
        super().show_speech_bubble(text)
        self.bubble_label.setWordWrap(text != self.hunger_text())
        self.bubble_label.setMaximumWidth(min(320,max(100,self.screen().availableGeometry().width()-40)))
        self.bubble_label.setStyleSheet('background:#FFF8E8;color:#294B3C;border:2px solid #789276;border-radius:14px;padding:12px;font:11pt "Microsoft YaHei UI";')
        self.speech_bubble.adjustSize(); self.update_bubble_position()
        self._bubble_timeout.start(duration)

    def update_bubble_position(self):
        bubble=getattr(self,'speech_bubble',None)
        if not bubble:return
        area=self.screen().availableGeometry()
        x=self.x()+(self.width()-bubble.width())//2
        y=self.y()-bubble.height()-10
        if y<area.top():y=self.y()+self.height()+10
        bubble.move(max(area.left(),min(x,area.right()+1-bubble.width())),max(area.top(),min(y,area.bottom()+1-bubble.height())))

    def closeEvent(self,event):
        self.save_position()
        if hasattr(self,'tray'):self.tray.hide()
        super().closeEvent(event)
