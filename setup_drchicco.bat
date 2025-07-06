@echo off
cd /d "%~dp0"

echo [🛠] Creo ambiente virtuale in 'venv'...
python -m venv venv

echo [✅] Ambiente virtuale creato. Attivo venv...
call venv\Scripts\activate

echo [📦] Installo le dipendenze da requirements.txt...
echo autogen> requirements.txt
echo pymed>> requirements.txt
echo pandas>> requirements.txt
echo openai>> requirements.txt
echo requests>> requirements.txt
echo streamlit>> requirements.txt
echo fpdf>> requirements.txt
echo matplotlib>> requirements.txt

pip install --upgrade pip
pip install -r requirements.txt

echo [✅] Setup completato. Puoi ora avviare l'app con:
echo.
echo    streamlit run app.py
echo.
pause
