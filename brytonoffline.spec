# -*- mode: python -*-


a = Analysis(['main.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          Tree('img/', 'img'),
          a.datas,
          name=os.path.join('dist', 'brytonoffline.exe'),
          debug=False,
          strip=None,
          upx=False,
          console=False, icon='img\\bryton_logo.ico')
app = BUNDLE(exe,
             name=os.path.join('dist', 'brytonoffline.exe.app'))

