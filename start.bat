@echo off
echo ========================================
echo  电影协同过滤推荐系统 - 启动向导
echo ========================================
echo.

echo [1/3] 安装后端依赖...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt -q

echo [2/3] 启动后端服务 (FastAPI)...
start "Backend" cmd /c "call .venv\Scripts\activate.bat && uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload"

echo 等待后端启动...
timeout /t 3 /nobreak >nul

echo [3/3] 启动前端服务 (Vue)...
cd frontend
if not exist "node_modules" (
    echo   安装前端依赖...
    call npm install
)
start "Frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo  启动完成！
echo  后端 API:  http://localhost:8000
echo  前端页面:  http://localhost:5173
echo  按任意键关闭本窗口...
echo ========================================
pause >nul
