# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
root = Path(SPECPATH)
a = Analysis(
    [str(root / '罗小黑桌宠.py')], pathex=[str(root)],
    binaries=[], datas=[(str(root / 'assets'), 'assets')],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32', 'PyQt5.QtMultimedia'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=['PIL'], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='罗小黑桌宠',
          debug=False, strip=False, upx=False, console=False,
          icon=str(root / 'assets' / 'lxh.ico'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='罗小黑桌宠_5.0')
