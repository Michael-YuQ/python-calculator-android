# 使用 BeeWare 构建 APK（Windows 友好）

BeeWare 是一个纯 Python 的跨平台框架，在 Windows 上构建 Android APK 更简单。

## 方法一：在 Windows 上构建（推荐）

### 1. 安装 BeeWare
```bash
pip install briefcase
```

### 2. 创建 Android 项目
```bash
briefcase create android
```

### 3. 构建 APK
```bash
briefcase build android
briefcase package android
```

### 4. APK 位置
生成的 APK 在：`android/gradle/Calculator/app/build/outputs/apk/`

---

## 方法二：使用 Colab（如果 Windows 构建失败）

在 Google Colab 中运行：

```python
# 安装 BeeWare
!pip install briefcase

# 克隆项目
!git clone https://github.com/Michael-YuQ/python-calculator-android.git
%cd python-calculator-android

# 安装 Android SDK 依赖
!apt-get update
!apt-get install -y openjdk-17-jdk wget unzip

# 下载 Android SDK
!wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
!unzip commandlinetools-linux-9477386_latest.zip -d android-sdk
!mkdir -p android-sdk/cmdline-tools/latest
!mv android-sdk/cmdline-tools/* android-sdk/cmdline-tools/latest/ 2>/dev/null || true

# 设置环境变量
import os
os.environ['ANDROID_HOME'] = '/content/python-calculator-android/android-sdk'
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'

# 构建 APK
!briefcase create android
!briefcase build android
!briefcase package android

# 下载 APK
from google.colab import files
import glob
apk_files = glob.glob('android/gradle/Calculator/app/build/outputs/apk/**/*.apk', recursive=True)
if apk_files:
    files.download(apk_files[0])
```

---

## 优点

- ✅ Windows 原生支持
- ✅ 不需要 WSL
- ✅ 构建速度较快
- ✅ 使用原生 UI 组件

## 缺点

- 需要下载 Android SDK（约 1-2GB）
- 首次构建需要较长时间

---

## 如果遇到问题

1. 确保安装了 Java JDK 17
2. 确保有足够的磁盘空间（至少 5GB）
3. 如果 Windows 构建失败，使用 Colab 方案
