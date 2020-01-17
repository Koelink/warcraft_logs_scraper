pyinstaller --onefile warcraft_logs.py
copy "dist\warcraft_logs.exe" "warcraft_logs.exe"
del "warcraft_logs.spec"
rd/S /Q "build"
rd/S /Q "dist"
rd/S /Q "__pycache__"
pause