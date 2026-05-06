@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

if not exist dist mkdir dist
pyinstaller --noconfirm --clean packaging\productivity_planner.spec

echo.
echo Build complete. EXE: dist\ProductivityPlanner.exe
endlocal
