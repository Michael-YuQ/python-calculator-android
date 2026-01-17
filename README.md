# Python 计算器 Android APK

这是一个使用 Python 和 Kivy 框架开发的计算器应用。

## 功能特性

- 基本算术运算：加、减、乘、除
- 小数点支持
- 清除功能
- 简洁的用户界面

## 本地测试

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python main.py
```

## 打包成 Android APK

### 方法一：使用 Buildozer（推荐在 Linux 上使用）

1. 安装 Buildozer：
```bash
pip install buildozer
```

2. 安装必要的系统依赖（Ubuntu/Debian）：
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

3. 初始化并构建 APK：
```bash
buildozer android debug
```

4. APK 文件将生成在 `bin/` 目录下

### 方法二：使用 Python-for-Android

```bash
pip install python-for-android
p4a apk --private . --package=org.example.calculator --name "Calculator" --version 1.0 --bootstrap=sdl2 --requirements=python3,kivy --permission INTERNET
```

### 方法三：使用在线服务

如果你在 Windows 上开发，可以使用以下在线服务：
- **Google Colab** + Buildozer
- **GitHub Actions** 自动构建

## 注意事项

- Buildozer 在 Linux 或 macOS 上运行最佳
- Windows 用户建议使用 WSL2（Windows Subsystem for Linux）
- 首次构建会下载 Android SDK/NDK，需要较长时间和稳定的网络连接
- 确保有足够的磁盘空间（至少 10GB）

## 应用截图

计算器包含以下功能按钮：
- 数字键：0-9
- 运算符：+、-、*、/
- 小数点：.
- 清除：C
- 等于：=
