@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
echo.
echo Installation abgeschlossen. Aktiviere die Umgebung mit: .venv\Scripts\activate
