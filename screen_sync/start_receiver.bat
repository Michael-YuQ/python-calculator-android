@echo off
REM Windows 接收端启动脚本

echo ==================================
echo 屏幕同步 - 接收端启动脚本
echo ==================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.6+
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

REM 参数
set SERVER_HOST=%1
set SERVER_PORT=%2

if "%SERVER_HOST%"=="" set SERVER_HOST=localhost
if "%SERVER_PORT%"=="" set SERVER_PORT=5003

echo.
echo 服务器: %SERVER_HOST%:%SERVER_PORT%
echo.

REM 启动接收端
python client_receiver.py %SERVER_HOST% %SERVER_PORT%

pause
