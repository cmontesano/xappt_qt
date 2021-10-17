@ECHO OFF

SETLOCAL

SET PYTHON3=C:\Python39\python.exe

FOR %%i in ("%~dp0.") DO SET "SCRIPT_PATH=%%~fi"

:uniqLoop
SET TEMP_PATH=%SCRIPT_PATH%\tmp%RANDOM%
if exist "%TEMP_PATH%" goto :uniqLoop
MKDIR %TEMP_PATH%

%PYTHON3% -m venv %TEMP_PATH%\venv

CALL %TEMP_PATH%\venv\Scripts\activate.bat

python -m pip install wheel
python -m pip install xappt xappt-qt
python -m pip install -r %SCRIPT_PATH%\requirements.txt

python %SCRIPT_PATH%\build.py

RMDIR /S /Q %TEMP_PATH%
