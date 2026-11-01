"""Notification audio: WAV fallback plus MP3/custom playback."""
from PyQt5 import QtCore
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QSoundEffect

class NotificationAudio(QtCore.QObject):
    failed = QtCore.pyqtSignal()
    def __init__(self,parent):
        super().__init__(parent)
        self.player=QMediaPlayer(self)
        self.fallback=QSoundEffect(self)
        self.player.error.connect(self._error)
        self._falling_back=False
    def setVolume(self,value):
        self.player.setVolume(round(value*100));self.fallback.setVolume(value)
    def stop(self):
        self.player.stop();self.fallback.stop()
    def play_file(self,path,default):
        self.stop();self._falling_back=False
        self.fallback.setSource(QtCore.QUrl.fromLocalFile(str(default)))
        if path==default:
            self.fallback.play();return
        self.player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(str(path))))
        self.player.play()
    def _error(self,*args):
        if self._falling_back:return
        self._falling_back=True
        self.player.stop();self.fallback.play();self.failed.emit()
