"""Card gallery for selecting role-specific animations; changes require confirmation."""
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from .storage import resource_path
from .config import ANIMATIONS
from .settings_ui import CapsuleCombo

NAMES = {'LXHflower':'抱花待机','LXHmiao':'喵喵','LXHroll':'向左滚动','LXHroll1':'向右滚动','LXHrun':'向左奔跑','LXHrunright':'向右奔跑','LXHeat':'吃饭','LXHwork':'工作','LXHheixiu':'嘿咻','LXHchicken':'小鸡','LXHconfuse':'疑惑','LXHhi':'打招呼','LXHno':'拒绝','LXHplay':'提起玩耍','LXHsanbu':'散步','LXHwalkright':'向右散步','LXHsatiate':'吃饱了','LXHtrampoline':'蹦床'}
for entry in ANIMATIONS.values():
    if 'label' in entry:NAMES[Path(entry['file']).stem]=entry['label']
ROLES=[('待机动作','idle'),('长按拖动动作','lift'),('下落动作','fall'),('工作动作','work')]

class AnimationGallery(QtWidgets.QWidget):
    def __init__(self,pet):
        super().__init__(pet);self.pet=pet;self.movie=None;self.selected=None
        self.setWindowTitle('小黑动作图鉴')
        area=pet.screen().availableGeometry();self.resize(min(1080,area.width()-40),min(780,area.height()-40))
        layout=QtWidgets.QVBoxLayout(self)
        top=QtWidgets.QHBoxLayout();top.addWidget(QtWidgets.QLabel('选择用途'))
        self.role=CapsuleCombo()
        for label,key in ROLES:self.role.addItem(label,key)
        top.addWidget(self.role);top.addStretch();layout.addLayout(top)
        import_button=QtWidgets.QPushButton('导入自己的待机动画')
        import_button.clicked.connect(self.import_idle)
        top.addWidget(import_button)
        body=QtWidgets.QHBoxLayout();layout.addLayout(body,1)
        self.cards=QtWidgets.QListWidget();self.cards.setViewMode(QtWidgets.QListView.IconMode)
        self.cards.setResizeMode(QtWidgets.QListView.Adjust);self.cards.setMovement(QtWidgets.QListView.Static)
        self.cards.setIconSize(QtCore.QSize(120,120));self.cards.setGridSize(QtCore.QSize(150,170));self.cards.setSpacing(6)
        self.cards.setWordWrap(True)
        self.cards.setStyleSheet('QListWidget {background:#F4EED9;border:none;border-radius:16px;padding:8px;} QListWidget::item {background:#FFF8E8;border:2px solid #E0D9BC;border-radius:18px;padding:6px;color:#365B45;} QListWidget::item:selected {background:#DCE8CC;border:2px solid #789276;}')
        body.addWidget(self.cards,1)
        side=QtWidgets.QVBoxLayout();body.addLayout(side)
        self.preview=QtWidgets.QLabel('选择卡片查看动画');self.preview.setFixedSize(230,230);self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setStyleSheet('background:#FFF8E8;border:2px solid #B4C49C;border-radius:18px;')
        side.addWidget(self.preview)
        self.name=QtWidgets.QLabel();self.name.setWordWrap(True);side.addWidget(self.name)
        self.current=QtWidgets.QLabel();self.current.setWordWrap(True);self.current.setMaximumWidth(230);side.addWidget(self.current)
        self.apply=QtWidgets.QPushButton('确认设置');self.apply.setEnabled(False);self.apply.clicked.connect(self.confirm);side.addWidget(self.apply)
        reset=QtWidgets.QPushButton('恢复此动作默认');reset.clicked.connect(self.reset);side.addWidget(reset)
        side.addWidget(QtWidgets.QLabel('选择仅作预览，确认后保存。'));side.addStretch()
        paths=list(sorted(resource_path('assets').glob('*.gif')))
        for path in paths:
            reader=QtGui.QImageReader(str(path));image=reader.read()
            if image.isNull():continue
            item=QtWidgets.QListWidgetItem(QtGui.QIcon(QtGui.QPixmap.fromImage(image)),NAMES.get(path.stem,path.stem[:18]))
            item.setData(QtCore.Qt.UserRole,str(path));item.setToolTip(path.name);self.cards.addItem(item)
        self.cards.currentItemChanged.connect(self.select)
        self.role.currentIndexChanged.connect(self.refresh_role)
        self.refresh_role()

    def stop_preview(self,*args):
        if self.movie:
            self.movie.stop();self.preview.setMovie(None);self.movie.deleteLater();self.movie=None

    def import_idle(self):
        self.pet.change_idle_gif()
        self.role.setCurrentIndex(0)
        self.refresh_role()

    def select(self,item,previous=None):
        self.stop_preview();self.apply.setEnabled(False)
        if not item:return
        path=item.data(QtCore.Qt.UserRole);movie=QtGui.QMovie(path)
        if not movie.isValid() or not movie.jumpToFrame(0):movie.deleteLater();return
        size=movie.currentImage().size();size.scale(210,210,QtCore.Qt.KeepAspectRatio);movie.setScaledSize(size)
        self.movie=movie;self.selected=path;self.preview.setMovie(movie);movie.start()
        self.name.setText(item.text());self.apply.setEnabled(True)

    def refresh_role(self,*args):
        role=self.role.currentData();path=self.pet.idle_gif_path if role=='idle' else self.pet.action_path(role)
        self.current.setText('当前：'+NAMES.get(Path(path).stem,Path(path).name))
        for index in range(self.cards.count()):
            item=self.cards.item(index)
            if Path(item.data(QtCore.Qt.UserRole))==Path(path):
                self.cards.setCurrentItem(item);return

    def confirm(self):
        if not self.selected:return
        check=QtGui.QImageReader(self.selected)
        if check.read().isNull():
            QtWidgets.QMessageBox.warning(self,'素材不可用','无法读取所选动画，请重新选择。');return
        role=self.role.currentData()
        if role=='idle':
            self.pet.settings['idle_gif']=self.selected;self.pet.idle_gif_path=self.selected
        else:self.pet.settings.setdefault('action_gifs',{})[role]=self.selected
        self.pet.store.save(self.pet.settings)
        from .state import PetState
        state={'idle':PetState.IDLE,'lift':PetState.DRAG,'fall':PetState.FALL,'eat':PetState.EAT,'work':PetState.WORK}[role]
        if self.pet.state==state:self.pet.loadGif(self.selected)
        self.refresh_role();self.current.setText(self.current.text()+'\n已保存')

    def reset(self):
        role=self.role.currentData()
        self.selected=self.pet._asset(ANIMATIONS[role]['file'])
        self.confirm()
