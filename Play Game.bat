@echo off
rem Double-click this file to start the game.
cd /d "%~dp0"
cd "2D-Arena-PvP-game-main"
python main.py
if errorlevel 1 pause
