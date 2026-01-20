from PyInstaller.compat import is_win, is_darwin

if is_win:
    icons = ['../src/icons/logo.ico', '../src/icons/alogo.ico']
    datas = [('../src/circos', 'circos')]

elif is_darwin:
    icons = ['../src/icons/logo.icns']
    datas = [('../src/circos', 'circos'), ('../src/icons/alogo.icns', '.')]

else:
    icons = ['../src/icons/logo.ico']
    datas = [('../src/circos', 'circos')]

a = Analysis(
    ['../src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Circhart',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icons,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Circhart',
)

if is_darwin:
    app = BUNDLE(
        coll,
        name = 'Circhart.app',
        icon = icons[0],
        bundle_identifier=None,
        info_plist={
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Circhart Project File',
                    'CFBundleTypeIconFile': 'alogo.icns',
                    'CFBundleTypeRole': 'Editor',
                    'LSHandlerRank': 'Owner',
                    'LSItemContentTypes': ['app.Circhart.circ']
                }
            ],
            'UTExportedTypeDeclarations': [
                {
                    'UTTypeIdentifier': 'app.Circhart.circ',
                    'UTTypeTagSpecification': {
                        'public.filename-extension': ['circ']
                    },
                    'UTTypeConformsTo': ['public.data'],
                    'UTTypeDescription': 'Circhart Project File',
                    'UTTypeIconFile': 'alogo.icns'
            }]
        }
    )
