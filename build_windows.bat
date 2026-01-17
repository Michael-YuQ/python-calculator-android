@echo off
echo 正在安装 python-for-android...
pip install python-for-android

echo.
echo 开始构建 APK...
p4a apk --private . --package=org.example.calculator --name "Calculator" --version 1.0 --bootstrap=sdl2 --requirements=python3,kivy --permission INTERNET --arch=armeabi-v7a

echo.
echo 构建完成！APK 文件在当前目录下
pause
