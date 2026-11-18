@echo off
setlocal
cd /d "%~dp0"
set "SMARTDUCK_MAKENSIS="
for /f "delims=" %%I in ('where makensis.exe 2^>nul') do if not defined SMARTDUCK_MAKENSIS set "SMARTDUCK_MAKENSIS=%%I"
if not defined SMARTDUCK_MAKENSIS if exist "%ProgramFiles(x86)%\NSIS\makensis.exe" set "SMARTDUCK_MAKENSIS=%ProgramFiles(x86)%\NSIS\makensis.exe"
if not defined SMARTDUCK_MAKENSIS if exist "%ProgramFiles%\NSIS\makensis.exe" set "SMARTDUCK_MAKENSIS=%ProgramFiles%\NSIS\makensis.exe"
if not defined SMARTDUCK_MAKENSIS (
  echo Instale o NSIS 3 para compilar os fontes do instalador.
  exit /b 1
)
if not exist dist mkdir dist
"%SMARTDUCK_MAKENSIS%" /V3 assistant.nsi
if errorlevel 1 exit /b 1
"%SMARTDUCK_MAKENSIS%" /V3 installer.nsi
if errorlevel 1 exit /b 1
echo Instalador criado: ..\SmartDuck_Instalar_1.9.0.exe
exit /b 0
