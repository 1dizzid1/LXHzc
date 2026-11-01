from PyQt5 import QtCore, QtGui, QtWidgets


DIALOG_STYLE = """
QDialog { background: #FFF8E8; color: #294B3C; }
QDialog QWidget { font-family: 'Microsoft YaHei UI', 'Microsoft YaHei'; font-weight: bold; }
QFrame#forestCard { background: #FFF8E8; border: 3px solid #789276; border-radius: 24px; }
QWidget#forestBody { background: #F4EED9; border-radius: 16px; }
QLabel#forestTitle { color: #365B45; font-size: 14pt; padding: 8px; }
QPushButton#forestClose { min-width: 0px; padding: 0px; border-radius: 16px; font-size: 16pt; }
QDialog QLabel { color: #294B3C; background: transparent; }
QDialog QLineEdit, QDialog QAbstractSpinBox {
    background: #FFFCF3; color: #294B3C;
    border: 2px solid #BECBA5; border-radius: 14px;
    padding: 8px 12px; min-height: 24px;
    selection-background-color: #DCE8CC; selection-color: #234D39;
}
QDialog QLineEdit:focus, QDialog QAbstractSpinBox:focus { border-color: #50785A; }
QDialog QPushButton {
    background: #DCE8CC; color: #365B45;
    border: 2px solid #A8BC91; border-bottom: 4px solid #A8BC91; border-radius: 16px;
    padding: 9px 18px; min-width: 64px;
}
QDialog QPushButton:hover { background: #CADDB6; border-color: #8FA87A; }
QDialog QPushButton:pressed { background: #B8D0A3; }
QDialog QPushButton:focus { border-color: #B0C58B; }
QDialog QPushButton:disabled { background: #E3E7D7; color: #85917E; border-color: #D2D9C4; }
QDialog QAbstractSpinBox::up-button { width: 22px; }
QDialog QAbstractSpinBox::down-button { width: 22px; }
"""


class RoundClose(QtWidgets.QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36,36)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def paintEvent(self,event):
        painter=QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('#789276'),2))
        painter.setBrush(QtGui.QColor('#DCE8CC' if self.underMouse() else '#FFF8E8'))
        painter.drawEllipse(QtCore.QRectF(2,2,32,32))
        painter.setPen(QtGui.QPen(QtGui.QColor('#365B45'),2.5,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap))
        painter.drawLine(13,13,23,23)
        painter.drawLine(23,13,13,23)


class CardTitle(QtWidgets.QLabel):
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton and hasattr(self, 'drag_offset'):
            self.window().move(event.globalPos() - self.drag_offset)
            event.accept()


class DialogTheme(QtCore.QObject):
    """Style tool dialogs when their layouts are ready; leave the pet and bubbles alone."""

    @staticmethod
    def bring_to_front(widget):
        # Run after show has completed, including dialogs opened from a menu.
        try:
            if widget.isVisible():
                widget.raise_()
                widget.activateWindow()
        except RuntimeError:
            pass  # The dialog may have been deleted before the queued callback.

    def eventFilter(self, widget, event):
        if (isinstance(widget, QtWidgets.QDialog)
                and widget.property('forestRounded')
                and event.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Show)):
            # Native window clipping gives rounded corners without a layered
            # (WA_TranslucentBackground) window or UpdateLayeredWindowIndirect.
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(widget.rect()), 24, 24)
            widget.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))
            if event.type() == QtCore.QEvent.Show:
                QtCore.QTimer.singleShot(0, lambda w=widget: self.bring_to_front(w))
        if (event.type() == QtCore.QEvent.Polish
                and isinstance(widget, QtWidgets.QDialog)
                and widget.isWindow()
                and not isinstance(widget, QtWidgets.QFileDialog)
                and not widget.windowFlags() & QtCore.Qt.FramelessWindowHint
                and not widget.property('forestStyled')):
            widget.setProperty('forestStyled', True)
            font = widget.font()
            font.setFamily('Microsoft YaHei UI')
            font.setPointSize(11)
            font.setBold(True)
            widget.setFont(font)
            widget.setStyleSheet(DIALOG_STYLE)
            widget.setMinimumWidth(360)
            if widget.layout():
                widget.layout().setContentsMargins(24, 22, 24, 22)
                widget.layout().setSpacing(16)
                # Transfer the existing content layout without changing its signals.
                body = QtWidgets.QWidget()
                body.setObjectName('forestBody')
                body.setLayout(widget.layout())
                # Native shadows can extend the dirty rectangle beyond the
                # translucent backing store on Windows. Keep the painted border.
                widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.FramelessWindowHint
                                      | QtCore.Qt.NoDropShadowWindowHint
                                      | QtCore.Qt.WindowStaysOnTopHint)
                widget.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
                widget.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
                widget.setProperty('forestRounded', True)
                outer = QtWidgets.QVBoxLayout(widget)
                outer.setContentsMargins(0, 0, 0, 0)
                card = QtWidgets.QFrame(widget)
                card.setObjectName('forestCard')
                outer.addWidget(card)
                content = QtWidgets.QVBoxLayout(card)
                content.setContentsMargins(18, 12, 18, 18)
                content.setSpacing(12)
                header = QtWidgets.QHBoxLayout()
                title = CardTitle(widget.windowTitle(), card)
                title.setObjectName('forestTitle')
                widget.windowTitleChanged.connect(title.setText)
                close = RoundClose(card)
                close.setObjectName('forestClose')
                close.setFixedSize(36, 36)
                close.setToolTip('关闭')
                close.setAccessibleName('关闭窗口')
                close.clicked.connect(widget.close)
                header.addWidget(title, 1)
                header.addWidget(close)
                content.addLayout(header)
                content.addWidget(body)
            for box in widget.findChildren(QtWidgets.QDialogButtonBox):
                for role, label in ((QtWidgets.QDialogButtonBox.Ok, '确定'),
                                    (QtWidgets.QDialogButtonBox.Cancel, '取消')):
                    button = box.button(role)
                    if button:
                        button.setText(label)
            if isinstance(widget, QtWidgets.QInputDialog):
                widget.setOkButtonText('确定')
                widget.setCancelButtonText('取消')
        return super().eventFilter(widget, event)
