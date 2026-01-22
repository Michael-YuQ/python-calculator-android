@echo off
REM 本地测试脚本 - 在同一台电脑上测试所有组件

echo ==================================
echo 屏幕同步 - 本地测试
echo ==================================
echo.
echo 此脚本将启动：
echo 1. 服务器
echo 2. 发送端
echo 3. 接收端
echo.
echo 按任意键开始...
pause >nul

REM 检查依赖
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

echo.
echo 启动服务器...
start "屏幕同步-服务器" cmd /k python server.py

timeout /t 2 /nobreak >nul

echo 启动发送端...
start "屏幕同步-发送端" cmd /k python client_sender.py localhost 5003 4

timeout /t 2 /nobreak >nul

echo 启动接收端...
start "屏幕同步-接收端" cmd /k python client_receiver.py localhost 5003

echo.
echo ✅ 所有组件已启动！
echo.
echo 💡 提示：
echo    - 服务器窗口显示连接状态
echo    - 发送端窗口显示发送统计
echo    - 接收端窗口显示屏幕画面
echo.
echo 关闭任意窗口即可停止对应组件
echo.
pause
