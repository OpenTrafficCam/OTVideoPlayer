cd %~dp0
python -m venv venv
call venv\Scripts\activate
timeout /T 1
pip install -r requirements.txt --no-cache-dir
timeout /T 10
deactivate
pause