# Build from this directory: python -m PyInstaller --clean --noconfirm LightControl.spec
from PyInstaller.utils.hooks import collect_submodules, copy_metadata
a = Analysis(['main.py'], pathex=[SPECPATH], binaries=[],
             datas=copy_metadata('flux_led'), hiddenimports=collect_submodules('flux_led'),
             hookspath=[], runtime_hooks=[], excludes=['PyQt5', 'PyQt6', 'tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='LightControl',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='LightControl')
