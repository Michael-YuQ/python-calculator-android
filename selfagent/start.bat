@echo off
echo ========================================
echo   SelfAgent - 启动开发服务器
echo ========================================
echo.

cd /d "%~dp0"

echo 检查 Node.js...
node -v >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 Node.js，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo 检查依赖...
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
)

echo.
echo 启动 Expo 开发服务器...
echo.
echo 提示:
echo   - 按 a 在 Android 模拟器中运行
echo   - 按 w 在浏览器中运行
echo   - 扫描二维码在手机 Expo Go 中运行
echo.
npx expo start

pause
