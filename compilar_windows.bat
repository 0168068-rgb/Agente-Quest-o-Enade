@echo off
chcp 65001 > nul
title Compilador AVALIA AutoBatch Windows & Instalador
echo ==========================================================
echo  GERANDO EXECUTAVEIS E INSTALADOR WINDOWS (.EXE)
echo ==========================================================

pip install pyinstaller pandas openpyxl playwright python-docx
python -m playwright install chromium
python build_windows_exe.py
python build_windows_installer_exe.py

echo.
echo ==========================================================
echo  Concluido com sucesso!
echo  1. Executavel Portatil: dist\AVALIA_AutoBatch\AVALIA_AutoBatch.exe
echo  2. Instalador .EXE: dist\AVALIA_AutoBatch_Setup_Instalador.exe
echo ==========================================================
pause
