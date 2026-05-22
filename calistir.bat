@echo off
chcp 65001 > nul 2>&1
title Yerel AI Asistan
cd /d "%~dp0"
python ai_asistan.py %*
pause