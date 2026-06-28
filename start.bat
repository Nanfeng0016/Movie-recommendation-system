@echo off
cd /d "%~dp0"

echo ========================================
echo  Movie Recommender - Startup
echo ========================================
echo.

REM Check venv
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual env .venv not found
    echo Run the following commands first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check frontend
if not exist "frontend\package.json" (
    echo [ERROR] frontend\package.json not found
    pause
    exit /b 1
)

echo [1/3] Installing backend dependencies...
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt -q
if %errorlevel% neq 0 (
    echo [WARN] pip install failed, trying to continue...
)

echo [2/3] Starting backend (FastAPI)...
start "Backend" cmd /c "cd /d "%~dp0" && call .venv\Scripts\activate.bat && uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend...
timeout /t 3 /nobreak >nul

echo [3/3] Starting frontend (Vue)...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo   Installing frontend dependencies...
    call npm install
)
start "Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo  All done!
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo ========================================
pause
