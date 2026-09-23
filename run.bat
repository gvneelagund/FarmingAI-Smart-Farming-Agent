@echo off
echo.
echo  ==========================================
echo   FarmingAI - Smart Farming Agent
echo  ==========================================
echo.

:: Check .env exists
if not exist ".env" (
    echo  [SETUP] Creating .env from template...
    copy .env.example .env
    echo.
    echo  ACTION REQUIRED:
    echo  Open .env file and replace:
    echo    GROQ_API_KEY=your_groq_api_key_here
    echo  with your actual key from https://console.groq.com
    echo.
    pause
)

:: Activate venv and run
echo  Starting FarmingAI...
call myenv\Scripts\activate.bat
streamlit run app.py

pause
