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

class AnimationMixin:
    def action_path(self, role):
        if role == 'eat':
            return self._asset(ANIMATIONS['eat']['file'])
        custom=self.settings.get('action_gifs',{}).get(role)
        return custom if custom and os.path.isfile(custom) else self._asset(ANIMATIONS[role]['file'])

    def open_gallery(self):
        self.open_settings()
        self._settings_dialog.navigation.setCurrentRow(3)

    def loadGif(self, path, size=None):
        if not os.path.isabs(path):
            path = str(resource_path(path))
        if self.gif and os.path.normcase(self.gif.fileName()) == os.path.normcase(path):
            self.gif.setPaused(getattr(self, '_hidden_sleep', False))
            return self.gif
        candidate = QtGui.QMovie(path)
        if not os.path.isfile(path) or not candidate.isValid() or not candidate.jumpToFrame(0):
            candidate.deleteLater()
            self.setToolTip('动画无法加载：' + path + '\n请检查素材文件，可右键更换待机动图。')
            if path not in self._failed_assets:
                self._failed_assets.add(path)
                logger.warning('Animation unavailable: %s', path)
            if self.gif is None:
                self.setFixedSize(180, 100)
                self.setText('小黑动画加载失败\n右键打开菜单')
            return self.gif
        self._failed_assets.discard(path)
        self.setToolTip('')
        old = self.gif
        self._natural_size = candidate.currentImage().size()
        candidate.setScaledSize(self._natural_size * self.scale_factor)
        self._resize_anchored(candidate.scaledSize())
        self.setText('')
        self.setMovie(candidate)
        self.gif = candidate
        candidate.setCacheMode(QtGui.QMovie.CacheNone)
        candidate.start()
        if getattr(self, '_hidden_sleep', False):candidate.setPaused(True)
        if old:
            old.stop()
            old.deleteLater()
        return candidate


    def set_scale_factor(self, factor):
        self.scale_factor = factor
        if self.gif:
            size = self._natural_size * factor
            self.gif.setScaledSize(size)
            self._resize_anchored(size)
        self.update_bubble_position()

        self.settings['scale'] = factor
        self.store.save(self.settings)

    def _asset(self, name):
        return str(resource_path('assets/' + name))

    def _resize_anchored(self, size):
        center_x = self.x() + self.width() / 2
        bottom = self.y() + self.height()
        self.setFixedSize(size)
        self.move(round(center_x - size.width() / 2), bottom - size.height())

    def change_idle_gif(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择新的待机动图', '', 'GIF 动图 (*.gif)')
        if not path:
            return
        probe = QtGui.QMovie(path)
        valid = probe.isValid() and probe.jumpToFrame(0)
        if not valid:
            probe.deleteLater()
            QtWidgets.QMessageBox.warning(self, '错误', '所选文件不是有效的 GIF 动画。')
            return
        preview = QtWidgets.QDialog(self)
        preview.setWindowTitle('预览待机动画')
        layout = QtWidgets.QVBoxLayout(preview)
        label = QtWidgets.QLabel()
        size = probe.currentImage().size()
        size.scale(320, 260, QtCore.Qt.KeepAspectRatio)
        probe.setScaledSize(size)
        label.setMovie(probe)
        layout.addWidget(label)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(preview.accept)
        buttons.rejected.connect(preview.reject)
        layout.addWidget(buttons)
        probe.start()
        accepted = preview.exec_() == QtWidgets.QDialog.Accepted
        probe.stop()
        probe.deleteLater()
        preview.deleteLater()
        if not accepted:
            return
        try:
            target = self.store.import_animation(path)
            self.idle_gif_path = str(target)
            self.settings['idle_gif'] = str(target)
            self.store.save(self.settings)
            self.startIdle()
        except OSError as exc:
            logger.exception('Import animation failed')
            QtWidgets.QMessageBox.warning(self, '错误', str(exc))
