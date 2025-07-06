@echo off
cd /d "%~dp0"
call venv\Scripts\activate
echo [✔] Ambiente virtuale attivato.
streamlit run app.py
