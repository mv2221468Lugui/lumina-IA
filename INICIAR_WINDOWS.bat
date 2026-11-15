@echo off
cd /d "%~dp0"
title Lumina AI 2050 - Inicializador
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py") else (set "PY=python")
%PY% --version || (echo Python nao encontrado. Instale Python e marque Add to PATH. & pause & exit /b 1)
%PY% -m pip install -r requirements.txt
if errorlevel 1 (echo Falha ao instalar dependencias. & pause & exit /b 1)
%PY% -m streamlit run app.py
pause
