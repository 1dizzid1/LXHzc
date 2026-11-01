"""Quiet mode, centralized settings and notification audio."""
import math
import struct
import wave
from PyQt5 import QtCore, QtWidgets
from .storage import logger

class ComfortMixin:
    def init_experience(self):
        self._hidden_sleep = False
        self._sound = None
        super().init_experience()
        self.setWindowOpacity(self.settings.get('opacity',1.0))
        quiet=self.tray.contextMenu().addAction('安静陪伴')
        menu=self.tray.contextMenu()
        exit_action=next(action for action in menu.actions() if action.text()=='退出')
        menu.removeAction(exit_action)
        menu.addAction(exit_action)
        quiet.setCheckable(True);quiet.setChecked(self.settings.get('quiet',False))
        quiet.toggled.connect(lambda value:self.set_option('quiet',value))
        self._quiet_action=quiet

    def set_option(self,key,value):
        super().set_option(key,value)
        if key=='quiet':
            if value:
                self.startIdle(); self._expire_bubble()
            self._resume_background()
            if hasattr(self,'_quiet_action'):
                self._quiet_action.blockSignals(True);self._quiet_action.setChecked(value);self._quiet_action.blockSignals(False)
        if key=='muted' and value and self._sound:self._sound.stop()

    def _resume_background(self):
        super()._resume_background()
        quiet=self.settings.get('quiet',False) or getattr(self,'_hidden_sleep',False)
        if quiet:
            for timer in (self.collectible_timer,self.collectible_check_timer,self.random_animation_timer):timer.stop()
        else:
            self.collectible_check_timer.setInterval(500)
            for timer,key,default in [(self.collectible_timer,'collect_seconds',180),(self.random_animation_timer,'random_minutes',37)]:
                timer.setInterval(int(self.settings.get(key,default)*(1000 if key=='collect_seconds' else 60000)))

    def hideEvent(self,event):
        super().hideEvent(event)
        if self._closing:return
        self._hidden_sleep=True
        self.timer.stop();self.changeDirectionTimer.stop()
        if self.gif:self.gif.setPaused(True)
        for item in self.collectibles:
            item.hide();item.movie_ref.setPaused(True)
        self._resume_background()

    def showEvent(self,event):
        super().showEvent(event)
        if getattr(self,'_hidden_sleep',False):
            self._hidden_sleep=False
            if self.is_working or self.is_eating:
                if self.gif:self.gif.setPaused(False)
            else:self.startIdle()
            for item in self.collectibles:
                item.show();item.movie_ref.setPaused(False)
            self._resume_background()

    def show_speech_bubble(self,text,priority=1,duration=5000):
        if self.settings.get('quiet',False) and priority<3:return
        super().show_speech_bubble(text,priority,duration)

    def notification_sound(self,kind='reminder',preview=False):
        if self.settings.get('muted',False) or self.settings.get('volume',0.5)<=0:return
        if not preview and not self.settings.get(kind+'_sound',True):return
        try:
            from .audio import NotificationAudio
            path=self.store.directory/'notification.wav'
            if not path.is_file():
                with wave.open(str(path),'wb') as output:
                    output.setparams((1,2,22050,0,'NONE','not compressed'))
                    output.writeframes(b''.join(struct.pack('<h',int(10000*math.sin(2*math.pi*660*i/22050)*math.sin(math.pi*i/8800))) for i in range(8800)))
            if self._sound is None:
                self._sound=NotificationAudio(self)
                self._sound.failed.connect(lambda: self.show_speech_bubble('所选音频无法播放，已使用默认提示音。',priority=3))
            self._sound.setVolume(self.settings.get('volume',0.5))
            from pathlib import Path
            selection=self.settings.get('sound_choice','default')
            selected=Path(self._asset('喵.MP3')) if selection=='meow' else Path(self.settings.get('custom_sound','')) if selection=='custom' else path
            if not selected.is_file():selected=path
            self._sound.play_file(selected,path)
        except Exception:
            logger.exception('Audio unavailable; visual notification retained')

    def closeEvent(self,event):
        if self._sound:self._sound.stop()
        super().closeEvent(event)

    def show_countdown_finished_dialog(self):
        self.notification_sound('countdown')
        super().show_countdown_finished_dialog()

    def open_settings(self):
        if self._raise_existing('_settings_dialog'):return
        from .settings_ui import build_settings
        self._settings_dialog=build_settings(self)
        self._settings_dialog.show()
