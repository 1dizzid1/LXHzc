import os
import sys
import PyQt5
plugins = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')
if sys.platform == 'win32':
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(plugins, 'platforms')
from PyQt5 import QtCore, QtGui, QtWidgets
QtCore.QCoreApplication.addLibraryPath(plugins)
from .animation import AnimationMixin
from .behavior import BehaviorMixin
from .clocks import ClocksMixin
from .view import ViewMixin
from .state import StateMixin, PetState
from .storage import SettingsStore
from .config import PARAMS, ANIMATIONS
from .experience import ExperienceMixin
from .comfort import ComfortMixin
from .activity import ActivityMixin

class KeyBridge(QtCore.QObject):
    pressed = QtCore.pyqtSignal(int)

class DeskPet(ActivityMixin, ComfortMixin, ExperienceMixin, StateMixin, AnimationMixin, BehaviorMixin, ClocksMixin, ViewMixin, QtWidgets.QLabel):
    def __init__(self, data_dir=None):
        super().__init__()
        self.store = SettingsStore(data_dir)
        self.store.configure_logging()
        self.settings = self.store.load()
        self.scale_factor = self.settings['scale']
        self.idle_gif_path = self.settings['idle_gif'] or self._asset(ANIMATIONS['idle']['file'])
        self._closing = False
        self._failed_assets = set()
        self._session = 0
        self.listener = self.gif = None
        self.state = PetState.IDLE
        self.collectibles, self.reminders = [], []
        self.collectible = None
        self.hunger_points = 100
        self.dragging = False
        self.moveSpeed = self.movingDirection = 0
        self.countdown_dialog = self.countdown_window = self.stopwatch_window = None
        self.countdown_time = None
        self._elapsed, self._started = 0.0, None
        self._bridge = KeyBridge(self)
        self._bridge.pressed.connect(self._count_key, QtCore.Qt.QueuedConnection)
        for name, callback in {
            'timer': self.updateAnimation, 'changeDirectionTimer': self.changeDirection,
            'collectible_timer': self.generate_collectible, 'collectible_check_timer': self.check_collectibles,
            'hunger_timer': self.update_hunger, '_random_end': self.end_random_animation,
            '_eating_timer': self.increase_hunger, 'countdown_timer': self.update_countdown,
            'stopwatch_timer': self.update_stopwatch, 'reminder_timer': self.check_reminders,
            'random_animation_timer': self.play_random_animation,
        }.items():
            timer = QtCore.QTimer(self)
            timer.timeout.connect(callback)
            setattr(self, name, timer)
        self._random_end.setSingleShot(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.NoDropShadowWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(500, 500, 120, 120)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.setMouseTracking(True)
        self.hunger_timer.start(PARAMS['hunger_interval'])
        self.reminder_timer.start(PARAMS['reminder_tick'])
        self.startIdle()
        self.init_experience()

def main():
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('LXHDeskPet.DesktopPet.5')
    app = QtWidgets.QApplication(sys.argv)
    from .storage import resource_path
    app.setApplicationName('小黑桌宠')
    app.setWindowIcon(QtGui.QIcon(str(resource_path('assets/lxh.ico'))))
    app.addLibraryPath(plugins)
    from dialog_theme import DialogTheme
    app.dialog_theme = DialogTheme(app)
    app.installEventFilter(app.dialog_theme)
    def cleanup_ui():
        app.removeEventFilter(app.dialog_theme)
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    app.aboutToQuit.connect(cleanup_ui)
    if '--self-test' in sys.argv:
        from .release_check import run
        return run(app)
    app.pet = DeskPet()
    app.pet.show()
    sys.exit(app.exec_())
