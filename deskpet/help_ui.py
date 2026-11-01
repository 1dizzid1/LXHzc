"""In-app instructions: each entry describes operation and observable feedback."""
from PyQt5 import QtCore, QtWidgets

SECTIONS = [
('基本操作', [
 ('打开菜单与设置','右击小黑打开快捷菜单；点击“设置”进入左侧分类面板。','切换分类即可调整外观、活动、声音或选择动作。'),
 ('点击与拖动','按住鼠标左键并移动小黑。普通模式松手回到待机；工作和吃饭时拖动保持原模式。','超过拖动距离后播放拖动动作。普通点击会结束当前动作、恢复待机。'),
 ('滚动与下落','右键选择“滚动”或“下落”；再次右键选择“停止”可回到待机。','滚动在屏幕边缘转向；下落停在屏幕可用区域底部。'),
 ('隐藏、找回与退出','右键选择“隐藏”；双击系统托盘小黑图标或右键托盘选择“显示小黑”找回。','隐藏不退出，提醒和计时继续。选择“退出”才关闭程序。系统托盘不可用时会最小化。'),
]),
('外观与动作', [
 ('大小与透明度','在“外观与大小”拖动滑杆。','百分比即时变化，自动保存；透明度滑杆越靠右越清晰。'),
 ('动作图鉴','先选用途，再点图片预览，最后点“确认设置”。','可更换待机、长按拖动、下落和工作动作；确认后保存，重启仍保留。吃饭动作固定不可更换。'),
 ('导入待机动画','在“动作图鉴”点击“导入自己的待机动画”，选择 GIF 并在预览框确认。','确认后应用为待机动画，复制到用户数据目录，不覆盖内置素材。取消不会改动。导入副本不在内置图鉴列表展示。'),
 ('手动播放动画','右键“播放动图”选择动作。','播放所选动画；普通点击小黑回到待机。'),
]),
('陪伴与活动', [
 ('自主散步与休息','在“陪伴与活动”调整自主活动程度，滑杆越靠右越活跃。','待机时按权重选择休息、散步或玩耍，动作持续时间会变化。低于 40 点更偏向休息，低于 15 点暂停自主散步和玩耍。'),
 ('跟我来','普通模式右键选择“跟我来”，再次右键选择“停止跟随”。','小黑跟随鼠标并保持约 70 像素距离；到达后停在原地继续播放跑步动作，两分钟后自动结束。点击、拖动或切换模式可中断；工作和吃饭期间不可开启。'),
 ('吃饭与饱食度状态','右键选择“吃饭”；再次右键可退出。选择“查看饱食度”显示当前状态。','吃饭每秒增加 1 点，最高 100；每两分钟减少 1 点。80–100 现在不饿，60–79 有点嘴馋，40–59 肚子饿了，15–39 好饿啊！，0–14 饿晕了。'),
 ('工作模式','右键开启工作模式，再次右键退出。','统计全局键盘按下次数；长按只算一次，松开再按才累计。组合键各键分别计数。监听启动失败会提示。'),
 ('随机小动作','在“陪伴与活动”开启“随机小动作”，滑杆越靠右越频繁。','默认每 37 分钟检查；待机时随机播放动作，3 分钟后恢复。拖动、吃饭、工作、手动动画期间不触发。'),
 ('嘿咻拾取','开启“嘿咻拾取”，滑杆越靠右出现越频繁。','默认每 3 分钟尝试生成，最多同时一只；小黑待机时前往拾取。已有个人频率设置优先保留。'),
 ('暂停自主活动','在托盘或设置开启“暂停自主活动”。','恢复待机并暂停随机动画和拾取；提醒与计时继续。关闭后恢复自主活动。'),
 ('安静陪伴','在托盘或设置开启“安静陪伴”。','暂停自主活动和普通状态气泡，保留重要提醒。声音是否播放仍由静音和声音开关控制。'),
]),
('提醒与计时', [
 ('添加与管理提醒','右键“添加提醒”，填写内容后选择未来日期与时间。“提醒列表”中可选中并删除。','到期显示通知并从待办中移除；退出后仍保存，错过的提醒下次启动补发一次。'),
 ('倒计时','右键“倒计时”，填写时长并确认。','重复打开会切回正在运行的窗口；结束弹出通知。关闭计时窗口即取消，退出程序不会保存倒计时。'),
 ('正计时','右键“正计时”，点击开始，可暂停、继续或停止。','按实际经过时间显示；重复打开复用窗口。关闭后停止，下次新开从零开始。'),
 ('气泡提示','状态提示会在小黑附近出现。','普通气泡自动消失；重要提醒优先，长提醒可在通知窗口中滚动查看全文。'),
]),
('声音与保存', [
 ('选择与试听声音','在“声音与提醒”选择轻柔短音、小黑喵叫或自选音频，点击试听。','音量滑杆即时调整。静音或零音量时试听也无声；提醒与倒计时可分别关闭声音。'),
 ('导入提示音','点击“导入自己的提示音”，选择不超过 20 MB 的 MP3 或 WAV。','文件复制到用户数据目录并保存选择；无法播放时回退默认短音，文字通知仍保留。'),
 ('自动保存与屏幕适配','大小、位置、动画选择与功能开关自动保存。','重启恢复设置；屏幕断开或可用区域变化时，小黑回到可见范围。隐藏时暂停动画更新，恢复后继续陪伴。'),
]),
]

def build_help():
    page=QtWidgets.QWidget();layout=QtWidgets.QVBoxLayout(page)
    tabs=QtWidgets.QTabWidget();layout.addWidget(tabs)
    tabs.setStyleSheet('QTabWidget::pane {border:none;background:#F4EED9;} QTabBar::tab {background:#F4EED9;color:#365B45;padding:10px 12px;border-radius:10px;} QTabBar::tab:selected {background:#DCE8CC;}')
    for title,entries in SECTIONS:
        scroll=QtWidgets.QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        content=QtWidgets.QWidget();rows=QtWidgets.QVBoxLayout(content);rows.setSpacing(14)
        for name,operation,feedback in entries:
            card=QtWidgets.QFrame();card.setObjectName('settingRow');box=QtWidgets.QVBoxLayout(card);box.setContentsMargins(18,16,18,16)
            box.addWidget(QtWidgets.QLabel(name))
            for prefix,text in [('怎么用：',operation),('会发生什么：',feedback)]:
                label=QtWidgets.QLabel(prefix+text);label.setWordWrap(True);label.setTextFormat(QtCore.Qt.PlainText)
                label.setStyleSheet('font-weight:normal;color:#52644B;');box.addWidget(label)
            rows.addWidget(card)
        rows.addStretch();scroll.setWidget(content);tabs.addTab(scroll,title)
    return page
