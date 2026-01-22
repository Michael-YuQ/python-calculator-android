@echo off
REM 启动远程控制客户端

echo ==================================
echo 远程控制客户端
echo ==================================
echo.
echo 服务器: 111.170.6.103
echo 屏幕共享端口: 5003
echo 命令接收端口: 5004
echo.
echo 功能:
echo - 接收服务器命令控制屏幕共享开关
echo - 接收文本命令并在 Kiro 中执行
echo.

REM 检查依赖
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

echo 启动中...
echo.

python remote_control_client.py

pause
