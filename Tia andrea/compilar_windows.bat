@echo off
chcp 65001 > nul
echo ======================================================================
echo   🎓 COMPILADOR DO LANÇADOR DE FREQUÊNCIA SOPHIA PARA WINDOWS
echo ======================================================================
echo.
echo 1. Instalando dependencias necessarias...
pip install -r requirements.txt
pip install pyinstaller customtkinter playwright
python -m playwright install chromium

echo.
echo 2. Gerando o arquivo Executavel (.exe)...
pyinstaller --noconsole --onefile --name="LancadorFrequenciaSophia" app_frequencia_sophia.py

echo.
echo ======================================================================
echo   ✅ SUCESSO! O arquivo LancadorFrequenciaSophia.exe foi gerado!
echo   Ele esta localizado na pasta "dist".
echo ======================================================================
pause
