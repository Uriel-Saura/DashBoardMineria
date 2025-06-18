@echo off
echo ==========================================
echo    DASHBOARD WEB - ANÁLISIS MAHJONG
echo ==========================================
echo.

echo Verificando dependencias...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Flask no está instalado. Instalando dependencias...
    pip install -r requirements_dashboard.txt
)

echo.
echo Iniciando dashboard web...
echo.
echo Abra su navegador en: http://localhost:5000
echo.
echo Presione Ctrl+C para detener el servidor
echo.

python dashboard_app.py

pause
