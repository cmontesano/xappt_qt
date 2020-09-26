@ECHO OFF
SET OLD_CWD=%cd%

SET SCRIPT_PATH=%~dp0
SET SCRIPT_PATH=%SCRIPT_PATH:~0,-1%
SET UI_PATH=%SCRIPT_PATH%\..\resources\ui
SET PY_PATH=%SCRIPT_PATH%\..\xappt_qt\gui\ui

cd %UI_PATH%

FOR %%I IN (*.ui) DO (pyside2-uic "%%I" -o "%PY_PATH%\%%~nI.py")

cd %OLD_CWD%
