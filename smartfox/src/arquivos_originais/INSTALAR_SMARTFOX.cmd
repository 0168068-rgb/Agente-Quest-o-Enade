@echo off
setlocal DisableDelayedExpansion
title SmartFox Autonomo - Instalacao
if not defined LOCALAPPDATA goto NO_PROFILE
if not exist "%~dp0extensao\manifest.json" goto NO_SOURCE
set "SF_ROOT=%LOCALAPPDATA%\SmartFox-Autonomo"
set "SF_TARGET=%LOCALAPPDATA%\SmartFox-Autonomo\extensao"
set "SF_STAGE=%LOCALAPPDATA%\SmartFox-Autonomo\preparacao-%RANDOM%-%RANDOM%"
set "SF_BACKUP=%LOCALAPPDATA%\SmartFox-Autonomo\extensao-anterior-%RANDOM%-%RANDOM%"
echo.
echo SmartFox Autonomo 11.2
echo Sem cadastro, chave de ativacao ou administrador do SmartFox.
echo Instalacao na pasta deste usuario do Windows.
echo.
if exist "%SF_STAGE%\" goto COPY_ERROR
if exist "%SF_BACKUP%\" goto COPY_ERROR
if not exist "%SF_ROOT%\" mkdir "%SF_ROOT%"
if not exist "%SF_ROOT%\" goto COPY_ERROR
xcopy "%~dp0extensao\*" "%SF_STAGE%\" /E /I /Y /Q >nul
if errorlevel 1 goto COPY_ERROR
if not exist "%SF_STAGE%\manifest.json" goto COPY_ERROR
if exist "%SF_TARGET%\" (
  move "%SF_TARGET%" "%SF_BACKUP%" >nul
  if errorlevel 1 goto COPY_ERROR
)
move "%SF_STAGE%" "%SF_TARGET%" >nul
if errorlevel 1 goto RESTORE
copy /Y "%~dp0COMECE_AQUI.html" "%SF_ROOT%\COMECE_AQUI.html" >nul
echo Arquivos preparados em:
echo "%SF_TARGET%"
echo.
echo FALTA APENAS ADICIONAR AO CHROME UMA VEZ:
echo 1. Abra chrome://extensions
echo 2. Ative Modo do desenvolvedor.
echo 3. Clique em Carregar sem compactacao.
echo 4. Selecione a pasta extensao mostrada acima.
echo.
echo Depois abra o AvaliA com seu login habitual e use Ferramentas.
echo O SmartFox nao vai pedir chave, senha propria ou liberacao.
echo.
start "" "%SF_ROOT%\COMECE_AQUI.html"
start "" explorer.exe "%SF_TARGET%"
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
  start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" "chrome://extensions"
  goto DONE
)
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "chrome://extensions"
  goto DONE
)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "chrome://extensions"
)
:DONE
echo Se ja usa o SmartFox antigo, exporte seu acervo e desative a versao antiga.
echo Nao remova a versao antiga antes de conferir seu backup.
echo Para atualizar esta edicao, mantenha a mesma pasta e clique em Recarregar.
pause
exit /b 0
:RESTORE
if exist "%SF_BACKUP%\" move "%SF_BACKUP%" "%SF_TARGET%" >nul
:COPY_ERROR
echo Nao foi possivel preparar os arquivos. Nenhum privilegio elevado foi solicitado.
echo Use a instalacao manual descrita em COMECE_AQUI.html.
pause
exit /b 1
:NO_PROFILE
echo A pasta de usuario do Windows nao foi localizada.
echo Use a instalacao manual descrita em COMECE_AQUI.html.
pause
exit /b 1
:NO_SOURCE
echo Extraia TODO o ZIP antes de executar este arquivo.
echo A pasta extensao deve ficar ao lado deste instalador.
pause
exit /b 1
