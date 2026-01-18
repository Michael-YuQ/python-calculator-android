"""
Google Colab 构建脚本
直接在 Colab 中运行此文件
"""

# 安装依赖
print("📦 安装 Python 依赖...")
import subprocess
subprocess.run(["pip", "install", "buildozer", "cython"], check=True)

# 克隆项目
print("📥 克隆项目...")
subprocess.run(["git", "clone", "https://github.com/Michael-YuQ/python-calculator-android.git"], check=True)

import os
os.chdir("python-calculator-android")

# 安装系统依赖
print("🔧 安装系统依赖...")
apt_packages = [
    "git", "zip", "unzip", "openjdk-17-jdk", "wget",
    "autoconf", "libtool", "pkg-config", "zlib1g-dev",
    "libncurses5-dev", "libncursesw5-dev", "libtinfo5",
    "cmake", "libffi-dev", "libssl-dev"
]
subprocess.run(["apt-get", "update"], check=True)
subprocess.run(["apt-get", "install", "-y"] + apt_packages, check=True)

# 构建 APK
print("🏗️ 开始构建 APK（这需要 15-20 分钟）...")
subprocess.run(["buildozer", "android", "debug"], check=True)

# 下载 APK
print("⬇️ 准备下载 APK...")
from google.colab import files

apk_files = [f for f in os.listdir('bin') if f.endswith('.apk')]
if apk_files:
    files.download(f'bin/{apk_files[0]}')
    print(f"✅ 成功！APK 已下载: {apk_files[0]}")
else:
    print("❌ 错误：未找到 APK 文件")
