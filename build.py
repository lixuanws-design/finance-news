"""PyInstaller build - windowed mode"""
import PyInstaller.__main__
import os

DIR = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    os.path.join(DIR, 'main.py'),
    '--name=财经热点日报',
    '--onedir',
    '--windowed',
    '--add-data', os.path.join(DIR, 'templates') + os.pathsep + 'templates',
    '--distpath', os.path.join(DIR, 'dist'),
    '--workpath', os.path.join(DIR, 'build_temp'),
    '--specpath', DIR,
    '--clean',
])
