"""Author credits and project provenance."""
from PyQt5 import QtCore, QtWidgets


def build_about():
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)
    layout.setContentsMargins(4, 4, 16, 4)
    layout.setSpacing(16)
    sections = [
        ('小黑桌宠 · 5.0', '这是一个出于个人爱好制作的《罗小黑战记》同人桌宠，希望小黑能陪伴你的日常。'),
        ('AI 辅助开发声明', '本项目使用 AI 辅助编写和修改代码：2025 年使用 DeepSeek，2026 年使用 Codex。功能想法、素材整理和体验调整由作者参与完成。欢迎反馈问题，一起完善小黑。'),
        ('角色与素材说明', '动图由作者从官方微博下载并进行抠图处理。罗小黑角色形象及相关素材版权归原权利人所有，本项目为非官方同人作品。桌宠仅出于个人爱好制作与二次分享，请勿用于商业用途。源码公开不代表对角色、美术或音频素材授予商业使用许可。'),
        ('联系作者', '小红书：@美味的灭蚊灯\n小红书号：4963293161\nGitHub：1dizzid1\n欢迎通过小红书联系，或在 GitHub 仓库反馈问题。'),
    ]
    for title, text in sections:
        card = QtWidgets.QFrame()
        card.setObjectName('settingRow')
        box = QtWidgets.QVBoxLayout(card)
        box.setContentsMargins(20, 18, 20, 18)
        box.addWidget(QtWidgets.QLabel(title))
        label = QtWidgets.QLabel(text)
        label.setTextFormat(QtCore.Qt.PlainText)
        label.setWordWrap(True)
        label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        label.setStyleSheet('font-weight:normal;color:#52644B;')
        box.addWidget(label)
        if title == '联系作者':
            link = QtWidgets.QLabel('<a href="https://github.com/1dizzid1/LXHzc" style="color:#365B45;">GitHub · LXHzc 源码与问题反馈 ↗</a>')
            link.setOpenExternalLinks(True)
            link.setWordWrap(True)
            box.addWidget(link)
        layout.addWidget(card)
    layout.addStretch()
    scroll.setWidget(page)
    return scroll
