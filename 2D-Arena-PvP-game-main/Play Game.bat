@echo off
rem Double-click this file to start the game.
cd /d "%~dp0"
python main.py
if errorlevel 1 pause
