@echo off
echo ========================================
echo Support Gatekeeper - Quick Setup
echo ========================================
echo.

echo Step 1: Checking if .env file exists...
if exist .env (
    echo [OK] .env file found
) else (
    echo [!] Creating .env file from template...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file and add your API keys:
    echo   - TWENTYI_API_TOKEN
    echo   - INTERCOM_SECRET_KEY
    echo   - INTERCOM_APP_ID
    echo   - SECRET_KEY
    echo.
    pause
)

echo.
echo Step 2: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 3: Running database migrations...
python manage.py migrate

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo Then visit: http://localhost:8000/
echo.
pause
