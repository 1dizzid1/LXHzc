# 小黑桌宠 5.0

《罗小黑战记》同人桌宠。

## 功能
自主散步与休息、跟随鼠标（停下时原地跑动）、吃饭与饱食度、工作陪伴、嘿咻拾取、提醒与计时、系统托盘、声音选择、动作图鉴、自定义动作及关于作者。

## 运行源码（Windows）
安装 Python 3.13，在源码目录执行：
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe 罗小黑桌宠.py
```
也可在创建环境后双击“启动小黑.bat”。

## 打包
建议将源码放在纯英文路径（如 D:\LXHzc），避免 Qt 5 插件路径解析问题。
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean deskpet.spec
```
输出 dist/罗小黑桌宠_5.0。请分发整个目录，不能只复制 EXE。
requirements-lock.txt 固定本次 Windows/Python 3.13 的构建依赖。

## 测试与数据
运行 tests/test_*.py 中的各脚本，可进行离屏回归测试。
个人设置、导入素材与提醒保存在 %LOCALAPPDATA%\LXHDeskPet\5.0，不应提交到仓库。
详细操作见“使用说明.txt”，也可在设置中打开“使用说明”。

## 关于和作者
2025 年使用 DeepSeek，2026 年使用 Codex 辅助开发。
小红书：@美味的灭蚊灯（小红书号 4963293161）
GitHub：https://github.com/1dizzid1/LXHzc

## 素材与使用说明
动图由作者从官方微博下载并抠图。角色形象及相关素材版权归原权利人所有，本项目为非官方同人作品，仅出于个人爱好制作和二次分享，请勿用于商业用途。
源码公开不代表角色、美术或音频素材获得商业授权。当前未指定开源许可证，公开可读不等于授予任意再利用许可。
