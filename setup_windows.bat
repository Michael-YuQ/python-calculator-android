@echo off
echo ========================================
echo Python 计算器 - Windows 环境配置
echo ========================================
echo.

echo 步骤 1: 安装 Python 依赖
pip install kivy python-for-android

echo.
echo 步骤 2: 需要安装的额外工具
echo.
echo 请确保已安装以下工具：
echo 1. Java JDK 8 或更高版本
echo    下载地址: https://www.oracle.com/java/technologies/downloads/
echo.
echo 2. Android SDK（可通过 Android Studio 安装）
echo    下载地址: https://developer.android.com/studio
echo.
echo 3. 设置环境变量：
echo    JAVA_HOME = JDK 安装路径
echo    ANDROID_HOME = Android SDK 路径
echo    PATH 中添加: %%ANDROID_HOME%%\tools 和 %%ANDROID_HOME%%\platform-tools
echo.
echo ========================================
echo 配置完成后，运行 build_windows.bat 构建 APK
echo ========================================
pause
