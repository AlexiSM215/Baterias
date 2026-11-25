@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Laboratorio de Baterias
echo Instalando dependencias (solo tarda la primera vez)...
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% -m pip install --upgrade -r requirements.txt
if errorlevel 1 (
  echo.
  echo No se encontro Python. Instalalo desde https://www.python.org/downloads/
  echo y marca la casilla "Add Python to PATH".
  pause
  exit /b 1
)
echo Abriendo el laboratorio en el navegador...
start "" cmd /c "timeout /t 6 >nul & start http://localhost:8501"
%PY% -m streamlit run Interactivo.py --server.headless true
pause
