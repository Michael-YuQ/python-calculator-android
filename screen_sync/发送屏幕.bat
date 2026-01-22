@echo off
REM 快速启动 - 发送屏幕到服务器

echo ==================================
echo 发送屏幕到服务器
echo ==================================
echo.
echo 服务器: 111.170.6.103:5003
echo 区域: 屏幕右侧 1/4
echo 帧率: 4 FPS
echo.

REM 检查依赖
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

echo 3 秒后开始发送...
timeout /t 3 /nobreak

python client_sender.py 111.170.6.103 5003 4

pause
