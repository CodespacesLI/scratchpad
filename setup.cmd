@echo off
rem Startet setup.ps1 ohne Aerger mit der PowerShell-Ausfuehrungsrichtlinie.
rem Aufruf: setup.cmd [claude^|codex^|beide^|pruefen]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
exit /b %ERRORLEVEL%
