ECHO Clean previous venv ...
powershell "if (Test-Path .\venv\) {Remove-Item .\venv\ -Recurse}"

ECHO Setting up new venv...
py -3.12 -m venv --clear venv

ECHO Installing dependancies...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip.exe install -r modules.txt
pause