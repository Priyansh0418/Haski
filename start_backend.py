#!/usr/bin/env python
import subprocess
import os
import sys

os.chdir(r'd:\Haski-main\backend')
venv_python = r'D:\Haski-main\.venv\Scripts\python.exe'
subprocess.run([venv_python, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8002'], cwd=r'd:\Haski-main\backend')
