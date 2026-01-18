# Python 项目打包成 Android APK 完整流程

## 📋 快速开始（3 步完成）

### 第 1 步：编写你的 Python 应用

在本地创建 `main.py`，编写你的应用代码（使用 Kivy 框架）

### 第 2 步：推送到 GitHub

```bash
git add main.py
git commit -m "Update app"
git push
```

### 第 3 步：在 Colab 构建 APK

访问 https://colab.research.google.com/ 运行构建脚本

---

## 📝 详细流程

### 一、本地开发

#### 1. 创建/修改你的应用代码

编辑 `main.py`，这是你的应用主文件。示例：

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.display = TextInput(readonly=True, font_size=32)
        layout.add_widget(self.display)
        
        # 添加你的界面和逻辑
        
        return layout

if __name__ == '__main__':
    MyApp().run()
```

#### 2. 本地测试（可选）

```bash
pip install kivy
python main.py
```

#### 3. 提交到 GitHub

```bash
git add main.py
git commit -m "描述你的修改"
git push
```

---

### 二、在 Colab 构建 APK

#### 1. 打开 Google Colab

访问：https://colab.research.google.com/

#### 2. 新建笔记本

点击 "新建笔记本" 或 "File" → "New notebook"

#### 3. 复制粘贴构建脚本

将以下完整脚本粘贴到 Colab 单元格中：

```python
# ========================================
# Python 转 Android APK 一键构建脚本
# ========================================

# 安装依赖
!pip install buildozer cython

# 克隆你的项目（替换成你的仓库地址）
!git clone https://github.com/Michael-YuQ/python-calculator-android.git
%cd python-calculator-android

# 安装系统依赖
!sudo apt-get update
!sudo apt-get install -y git zip unzip openjdk-17-jdk wget autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 构建 APK
!buildozer android debug

# 下载 APK
from google.colab import files
import os

apk_files = [f for f in os.listdir('bin') if f.endswith('.apk')]
if apk_files:
    files.download(f'bin/{apk_files[0]}')
    print(f"✅ 成功！APK 已下载: {apk_files[0]}")
else:
    print("❌ 未找到 APK 文件")
```

#### 4. 运行脚本

点击单元格左侧的 ▶️ 播放按钮，或按 `Shift + Enter`

#### 5. 等待完成

- 总时间：约 20-30 分钟
- APK 会自动下载到你的电脑

---

### 三、安装到手机

1. 将下载的 `.apk` 文件传输到 Android 手机
2. 在手机上打开文件管理器
3. 点击 APK 文件
4. 允许"未知来源"安装（如果提示）
5. 点击"安装"

---

## 🎯 以后每次修改的流程

1. **修改代码**：编辑 `main.py`
2. **推送代码**：`git push`
3. **打开 Colab**：运行构建脚本
4. **下载 APK**：自动下载
5. **安装测试**：传到手机安装

---

## ⚙️ 自定义配置

### 修改应用名称和包名

编辑 `buildozer.spec`：

```ini
[app]
title = 你的应用名称
package.name = yourappname
package.domain = com.yourname
```

### 修改应用图标

1. 准备一个 `icon.png`（建议 512x512）
2. 在 `buildozer.spec` 中设置：
```ini
icon.filename = %(source.dir)s/icon.png
```

### 添加 Python 依赖

在 `buildozer.spec` 中：
```ini
requirements = python3,kivy,requests,其他库
```

---

## 🔧 常见问题

### Q: 构建失败怎么办？
A: 查看错误日志，通常是依赖问题。在 Colab 中运行：
```python
!tail -100 .buildozer/android/platform/build-arm64-v8a/build.log
```

### Q: APK 没有下载？
A: 检查 bin 目录：
```python
!ls -la bin/
```

### Q: 可以在 Windows 本地构建吗？
A: 不推荐，配置复杂。Colab 是最简单的方案。

### Q: 构建时间太长？
A: 首次构建需要下载 SDK，后续会快很多。

---

## 📦 项目文件说明

```
python-calculator-android/
├── main.py              # 你的应用主文件（必需）
├── buildozer.spec       # 构建配置文件（必需）
├── requirements.txt     # Python 依赖
├── icon.png            # 应用图标（可选）
└── README.md           # 项目说明
```

---

## 💡 提示

- ✅ Colab 完全免费
- ✅ 不需要本地配置环境
- ✅ 支持所有 Kivy 功能
- ✅ 可以添加任何 Python 库
- ⚠️ 首次构建约 30 分钟
- ⚠️ Colab 会话有时间限制（12 小时）

---

## 🚀 进阶：自动化构建

使用 GitHub Actions 自动构建（参考 `.github/workflows/build.yml`）

每次 push 代码后，GitHub 会自动构建 APK，无需手动操作！
