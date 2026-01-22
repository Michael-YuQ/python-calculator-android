@echo off
echo 使用 Docker 构建 APK（无需配置复杂环境）
echo.
echo 请确保已安装 Docker Desktop for Windows
echo 下载地址: https://www.docker.com/products/docker-desktop
echo.

docker run --rm -v "%cd%":/app kivy/buildozer android debug
