@echo off
title PRETIUM AI - PROTOCOL AUTOMATIC
color 0A

echo.
echo ==========================================
echo   ROBOT MASSIU: INICIANT CERCA DE PREUS
echo ==========================================
echo.
"C:/Users/Usuari/AppData/Local/Programs/Python/Python314/python.exe" "d:/IA/COMPARADOR-PREUS/robot_massiu.py"

echo.
echo ==========================================
echo   GENERANT LA NOVA WEB...
echo ==========================================
echo.
"C:/Users/Usuari/AppData/Local/Programs/Python/Python314/python.exe" "d:/IA/COMPARADOR-PREUS/actualitzar_web.py"

echo.
echo ==========================================
echo   ✅ FEINA ACABADA! ELS FITXERS ESTAN LLESTOS.
echo ==========================================
echo.
timeout /t 10