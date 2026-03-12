#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""财经热点日报 - 启动入口"""
import os, sys, webbrowser, threading, time

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    TPL = os.path.join(sys._MEIPASS, 'templates')
    os.environ['_OC_TPL'] = TPL
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TPL = os.path.join(BASE_DIR, 'templates')

sys.path.insert(0, BASE_DIR)

def open_browser():
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8899')

if __name__ == '__main__':
    from app import app
    if os.environ.get('_OC_TPL'):
        app.template_folder = os.environ['_OC_TPL']
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="127.0.0.1", port=8899, debug=False, use_reloader=False)
