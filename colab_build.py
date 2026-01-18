"""
Python 转 Android APK - Colab 构建脚本

使用方法：
1. 在 Google Colab 中新建笔记本
2. 复制此文件内容到单元格
3. 修改下面的配置
4. 运行单元格

作者：Michael-YuQ
"""

# ========================================
# 配置区域（修改这里）
# ========================================

# 你的 GitHub 仓库地址
GITHUB_REPO = "https://github.com/Michael-YuQ/python-calculator-android.git"

# 仓库名称（URL 最后的部分）
REPO_NAME = "python-calculator-android"

# ========================================
# 以下代码无需修改
# ========================================

print("🚀 开始构建 Android APK...")
print(f"📦 仓库: {GITHUB_REPO}")
print("⏱️  预计时间: 20-30 分钟\n")

# 步骤 1: 安装 Python 依赖
print("📥 [1/5] 安装 Python 依赖...")
!pip install -q buildozer cython
print("✅ Python 依赖安装完成\n")

# 步骤 2: 克隆项目
print("📥 [2/5] 克隆项目...")
!git clone {GITHUB_REPO}
%cd {REPO_NAME}
print("✅ 项目克隆完成\n")

# 步骤 3: 安装系统依赖
print("📥 [3/5] 安装系统依赖...")
!sudo apt-get update -qq
!sudo apt-get install -y -qq git zip unzip openjdk-17-jdk wget autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
print("✅ 系统依赖安装完成\n")

# 步骤 4: 构建 APK
print("🔨 [4/5] 构建 APK（这需要 15-20 分钟）...")
!buildozer android debug
print("✅ APK 构建完成\n")

# 步骤 5: 下载 APK
print("📥 [5/5] 准备下载 APK...")
from google.colab import files
import os

apk_files = [f for f in os.listdir('bin') if f.endswith('.apk')]

if apk_files:
    apk_name = apk_files[0]
    print(f"✅ 找到 APK: {apk_name}")
    print(f"📦 文件大小: {os.path.getsize(f'bin/{apk_name}') / 1024 / 1024:.2f} MB")
    print("⬇️  开始下载...")
    files.download(f'bin/{apk_name}')
    print("\n" + "="*50)
    print("🎉 构建成功！APK 已下载到你的电脑")
    print("="*50)
    print("\n📱 下一步：")
    print("1. 将 APK 传输到 Android 手机")
    print("2. 在手机上点击 APK 文件")
    print("3. 允许安装未知来源应用")
    print("4. 点击安装")
    print("\n✨ 完成！")
else:
    print("❌ 错误：未找到 APK 文件")
    print("📋 查看构建日志:")
    !ls -la bin/
    print("\n可能的原因：")
    print("1. 构建失败 - 检查上面的错误信息")
    print("2. main.py 有语法错误")
    print("3. buildozer.spec 配置错误")
