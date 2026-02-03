@echo off
echo ============================================
echo  GravureStudioV1 - Module Guillochage
echo ============================================
echo.
echo Demarrage du module...
echo.
python guillochage_main.py
if errorlevel 1 (
    echo.
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo Installez Python 3.8+ depuis python.org
    echo.
    pause
)
