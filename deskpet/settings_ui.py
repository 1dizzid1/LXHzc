from PyQt5 import QtCore, QtGui, QtWidgets

STYLE = '''
QWidget#settingsContent QWidget { font-size:12pt; }
QWidget#settingsContent, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget { background:#F4EED9; border:none; }
QFrame#settingRow { background:#FFF8E8; border-radius:14px; }
QWidget#settingsContent QPushButton { background:#FFF8E8; border:2px solid #B4C49C; border-bottom:4px solid #B4C49C; }
QWidget#settingsContent QPushButton:hover { background:#F4EED9; }
QLabel#hint { color:#829078; font-size:11pt; font-weight:normal; }
QListWidget#navigation { background:#365B45; color:#FFF4D6; border:none; border-radius:18px; padding:10px; outline:0; }
QListWidget#navigation::item { padding:18px 12px; border-radius:14px; margin:6px 0; }
QListWidget#navigation::item:selected { background:#DCE8CC; color:#294B3C; }
QSlider::groove:horizontal { height:8px; background:#DEDCC4; border-radius:4px; }
QSlider::sub-page:horizontal { background:#A9C18E; border-radius:4px; }
QSlider::handle:horizontal { background:#FFF8E8; border:3px solid #789276; width:18px; margin:-8px 0; border-radius:12px; }
QSlider::handle:horizontal:focus { border-color:#365B45; }
QScrollBar:vertical { background:#F3EDD8; width:8px; border:none; }
QScrollBar::handle:vertical { background:#B5C59D; border-radius:4px; min-height:24px; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
'''

class RoundedChoiceMenu(QtWidgets.QMenu):
    def showEvent(self, event):
        super().showEvent(event)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 16, 16)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))


class CapsuleCombo(QtWidgets.QComboBox):
    """Painted capsule with a matching popup; keeps combo selection signals."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(178, 42)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._expanded = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('#789276' if self.hasFocus() else '#B4C49C'), 2))
        painter.setBrush(QtGui.QColor('#FFF8E8'))
        painter.drawRoundedRect(QtCore.QRectF(self.rect()).adjusted(1,1,-1,-1), 20, 20)
        painter.setPen(QtGui.QColor('#365B45'))
        painter.drawText(self.rect().adjusted(18,0,-36,0), QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, self.currentText())
        x, y = self.width()-23, self.height()//2
        direction = -1 if self._expanded else 1
        triangle = QtGui.QPolygonF([QtCore.QPointF(x-5,y-3*direction), QtCore.QPointF(x+5,y-3*direction), QtCore.QPointF(x,y+3*direction)])
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor('#789276'))
        painter.drawPolygon(triangle)

    def showPopup(self):
        menu = RoundedChoiceMenu(self)
        menu.setWindowFlags(menu.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        menu.setMinimumWidth(max(220, self.width()))
        menu.setStyleSheet('''
            QMenu { background:#FFF8E8; color:#365B45; border:2px solid #B4C49C;
                border-radius:16px; padding:8px; font: bold 12pt "Microsoft YaHei UI"; }
            QMenu::item { padding:12px 20px; margin:2px; border-radius:10px; }
            QMenu::item:selected { background:#DCE8CC; }
            QMenu::separator { height:1px; background:#DEDCC4; margin:2px 12px; }
        ''')
        actions = []
        for index in range(self.count()):
            if index: menu.addSeparator()
            action = menu.addAction(('●  ' if index == self.currentIndex() else '○  ') + self.itemText(index))
            actions.append(action)
        if self.currentIndex() >= 0: menu.setActiveAction(actions[self.currentIndex()])
        self._expanded = True
        self.update()
        try:
            selected = menu.exec_(self.mapToGlobal(QtCore.QPoint(0,self.height()+6)))
            if selected in actions: self.setCurrentIndex(actions.index(selected))
        finally:
            self._expanded = False
            self.update()
            menu.deleteLater()


class Toggle(QtWidgets.QAbstractButton):
    def __init__(self,checked,parent=None):
        super().__init__(parent);self.setCheckable(True);self.setChecked(checked)
        self.setFixedSize(56,30);self.setCursor(QtCore.Qt.PointingHandCursor)
    def paintEvent(self,event):
        p=QtGui.QPainter(self);p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setPen(QtGui.QPen(QtGui.QColor('#789276'),2))
        p.setBrush(QtGui.QColor('#789276' if self.isChecked() else '#DDDCC4'))
        p.drawRoundedRect(1,1,54,28,14,14)
        p.setPen(QtCore.Qt.NoPen);p.setBrush(QtGui.QColor('#FFF8E8'))
        p.drawEllipse(30 if self.isChecked() else 5,5,20,20)
        if self.hasFocus():
            p.setBrush(QtCore.Qt.NoBrush);p.setPen(QtGui.QPen(QtGui.QColor('#294B3C'),1,QtCore.Qt.DotLine));p.drawRoundedRect(3,3,50,24,12,12)


def build_settings(pet):
    dialog=QtWidgets.QDialog(pet);dialog.setWindowTitle('小黑的森林小屋 · 设置')
    available=pet.screen().availableGeometry()
    dialog.resize(min(1320,available.width()-40),min(820,available.height()-40))
    outer=QtWidgets.QHBoxLayout(dialog)
    content=QtWidgets.QWidget();content.setObjectName('settingsContent');content.setStyleSheet(STYLE)
    outer.addWidget(content);body=QtWidgets.QHBoxLayout(content);body.setContentsMargins(12,12,12,12);body.setSpacing(28)
    nav=QtWidgets.QListWidget();nav.setObjectName('navigation');nav.setFixedWidth(185)
    nav.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    nav.addItems(['外观与大小','陪伴与活动','声音与提醒','动作图鉴','使用说明','关于和作者']);body.addWidget(nav)
    pages=QtWidgets.QStackedWidget();body.addWidget(pages,1)
    layouts=[]
    for _ in range(3):
        scroll=QtWidgets.QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        page=QtWidgets.QWidget();layout=QtWidgets.QVBoxLayout(page);layout.setContentsMargins(4,4,16,4);layout.setSpacing(16)
        scroll.setWidget(page);pages.addWidget(scroll);layouts.append(layout)
    def row(page,title,hint=''):
        frame=QtWidgets.QFrame();frame.setObjectName('settingRow');box=QtWidgets.QHBoxLayout(frame);box.setContentsMargins(16,14,16,14)
        labels=QtWidgets.QVBoxLayout();labels.addWidget(QtWidgets.QLabel(title))
        if hint:
            label=QtWidgets.QLabel(hint);label.setObjectName('hint');label.setWordWrap(True);labels.addWidget(label)
        box.addLayout(labels,1);layouts[page].addWidget(frame);return box
    def slider(page,title,key,default,low,high,decode,encode,describe,hint=''):
        box=row(page,title,hint);right=QtWidgets.QHBoxLayout();right.setSpacing(12);value=pet.settings.get(key,default)
        label=QtWidgets.QLabel(describe(value));label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label.setMinimumWidth(72)
        control=QtWidgets.QSlider(QtCore.Qt.Horizontal);control.setRange(low,high);control.setValue(encode(value));control.setMinimumWidth(180);control.setMinimumHeight(30);control.setAccessibleName(title)
        def change(position):
            value=decode(position);label.setText(describe(value));pet.settings[key]=value
            if key=='scale':pet.set_scale_factor(value)
            elif key=='opacity':pet.setWindowOpacity(value)
            elif key=='volume' and pet._sound:pet._sound.setVolume(value)
            pet.store.save(pet.settings);pet._resume_background()
        control.valueChanged.connect(change);right.addWidget(control,1);right.addWidget(label);box.addLayout(right)
    slider(0,'小黑大小','scale',1,50,200,lambda n:n/100,lambda n:round(n*100),lambda n:f'{round(n*100)}%')
    slider(0,'小黑透明度','opacity',1,20,100,lambda n:n/100,lambda n:round(n*100),lambda n:f'{round(n*100)}%','向右拖动，看得更清楚')
    def action(page,title,callback):
        button=QtWidgets.QPushButton(title);button.clicked.connect(callback);layouts[page].addWidget(button)
    for key,title,default,page,hint in [('quiet','安静陪伴',False,1,'暂停自主活动，保留重要提醒'),('paused','暂停自主活动',False,1,''),('random_enabled','随机小动作',True,1,''),('collectibles_enabled','嘿咻拾取',True,1,''),('muted','静音',False,2,''),('reminder_sound','提醒提示音',True,2,''),('countdown_sound','倒计时提示音',True,2,'')]:
        box=row(page,title,hint);toggle=Toggle(pet.settings.get(key,default));toggle.setAccessibleName(title);toggle.toggled.connect(lambda checked,k=key:pet.set_option(k,checked));box.addWidget(toggle)
    activity=lambda n:'偶尔' if n>=60 else ('适中' if n>=15 else '活跃')
    slider(1,'自主活动程度','activity_level',2,1,3,int,int,lambda n:{1:'安静',2:'适中',3:'活跃'}[int(n)],'影响散步和玩耍的频率')
    slider(1,'小动作频率','random_minutes',37,1,240,lambda n:241-n,lambda n:round(241-n),activity,'向右拖动，更活跃')
    slider(1,'嘿咻出现频率','collect_seconds',180,10,600,lambda n:610-n,lambda n:round(610-n),lambda n:'偶尔' if n>=180 else ('适中' if n>=45 else '经常'),'向右拖动，更频繁')
    slider(2,'提示音量','volume',.5,0,100,lambda n:n/100,lambda n:round(n*100),lambda n:'无声' if n==0 else f'{round(n*100)}%')
    sounds=CapsuleCombo()
    sounds.setAccessibleName('提示音选择')
    for label,key in [('轻柔短音','default'),('小黑喵叫','meow'),('自选音频','custom')]:sounds.addItem(label,key)
    sounds.setCurrentIndex(max(0,sounds.findData(pet.settings.get('sound_choice','default'))))
    def select_sound(index):
        pet.settings['sound_choice']=sounds.itemData(index)
        pet.store.save(pet.settings)
    sounds.currentIndexChanged.connect(select_sound)
    row(2,'提示音').addWidget(sounds)
    def import_sound():
        from pathlib import Path
        import shutil, uuid
        source,_=QtWidgets.QFileDialog.getOpenFileName(dialog,'选择提示音','','音频 (*.mp3 *.MP3 *.wav *.WAV)')
        if not source:return
        try:
            source=Path(source)
            if source.stat().st_size>20*1024*1024:raise ValueError('请选择小于 20 MB 的音频。')
            folder=pet.store.directory/'sounds';folder.mkdir(exist_ok=True)
            target=folder/(uuid.uuid4().hex+source.suffix.lower());shutil.copy2(source,target)
            pet.settings['custom_sound']=str(target)
            pet.settings['sound_choice']='custom';pet.store.save(pet.settings)
            sounds.setCurrentIndex(sounds.findData('custom'))
            pet.notification_sound(preview=True)
        except (OSError,ValueError) as exc:
            QtWidgets.QMessageBox.warning(dialog,'导入失败',str(exc))
    action(2,'导入自己的提示音',import_sound)
    action(2,'试听提示音',lambda:pet.notification_sound(preview=True));action(2,'查看提醒列表',pet.manage_reminders)
    for layout in layouts:layout.addStretch()
    from .gallery import AnimationGallery
    gallery=AnimationGallery(pet)
    gallery.setWindowFlags(QtCore.Qt.Widget)
    pages.addWidget(gallery)
    from .help_ui import build_help
    pages.addWidget(build_help())
    from .about_ui import build_about
    pages.addWidget(build_about())
    dialog.gallery=gallery
    dialog.navigation=nav
    def switch_page(index):
        pages.setCurrentIndex(index)
        if index==3:
            if gallery.movie:gallery.movie.setPaused(False)
        elif gallery.movie:gallery.movie.setPaused(True)
    nav.currentRowChanged.connect(switch_page)
    dialog.finished.connect(gallery.stop_preview)
    nav.setCurrentRow(0)
    switch_page(0)
    return dialog
