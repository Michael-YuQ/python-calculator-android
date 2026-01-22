@echo off
REM 连接到服务器 111.170.6.103:5003

echo ==================================
echo 屏幕同步 - 连接到服务器
echo ==================================
echo.
echo 服务器地址: 111.170.6.103:5003
echo.

REM 检查依赖
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

echo 请选择模式:
echo [1] 发送端 - 分享我的屏幕
echo [2] 接收端 - 查看远程屏幕
echo.
set /p choice=请输入选择 (1 或 2): 

if "%choice%"=="1" (
    echo.
    echo 启动发送端...
    python client_sender.py 111.170.6.103 5003 4
) else if "%choice%"=="2" (
    echo.
    echo 启动接收端...
    python client_receiver.py 111.170.6.103 5003
) else (
    echo.
    echo ❌ 无效选择
    pause
    exit /b 1
)

pause
