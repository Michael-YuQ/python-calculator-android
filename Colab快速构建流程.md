# Google Colab 快速构建 Android APK 流程

## 📋 准备工作

1. 编写好你的 Python 应用代码（`main.py`）
2. 确保代码在本地可以运行
3. 提交到 GitHub

---

## 🚀 快速构建步骤

### 步骤 1：编写代码并提交到 GitHub

```bash
# 在本地修改 main.py
# 然后提交到 GitHub
git add main.py
git commit -m "更新应用代码"
git push
```

### 步骤 2：打开 Google Colab

访问：https://colab.research.google.com/

### 步骤 3：创建新笔记本

点击 "新建笔记本"

### 步骤 4：复制粘贴构建脚本

将 `colab_build.py` 的内容复制到 Colab 单元格中，然后运行

或者直接运行：

```python
# 一键构建脚本
!pip install buildozer cython==0.29.33

# 克隆你的项目（修改成你的仓库地址）
!git clone https://github.com/Michael-YuQ/python-calculator-android.git
%cd python-calculator-android

# 安装系统依赖
!sudo apt-get update -qq
!sudo apt-get install -y -qq git zip unzip openjdk-17-jdk wget autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 构建 APK
!buildozer -v android debug

# 自动查找并下载 APK
from google.colab import files
import glob

apk_files = glob.glob('bin/*.apk')
if not apk_files:
    apk_files = glob.glob('.buildozer/**/outputs/apk/**/*.apk', recursive=True)

if apk_files:
    print(f"✅ 找到 {len(apk_files)} 个 APK 文件")
    for apk in apk_files:
        print(f"📥 下载: {apk}")
        files.download(apk)
else:
    print("❌ 未找到 APK，查看错误日志:")
    !tail -100 .buildozer/android/platform/build-arm64-v8a/build.log
```

### 步骤 5：等待构建完成

- 首次构建：约 20-30 分钟
- 后续构建：约 10-15 分钟

### 步骤 6：下载 APK

构建完成后，APK 会自动下载到你的电脑

---

## 📱 安装到手机

1. 将 APK 传输到 Android 手机
2. 在手机上打开文件管理器
3. 点击 APK 文件
4. 允许"未知来源"安装
5. 完成安装

---

## 🔧 自定义配置

### 修改应用名称

编辑 `buildozer.spec`：

```ini
title = 你的应用名称
package.name = yourappname
package.domain = com.yourname
```

### 修改应用图标

1. 准备一个 `icon.png`（建议 512x512）
2. 放在项目根目录
3. 在 `buildozer.spec` 中添加：

```ini
icon.filename = icon.png
```

### 添加权限

在 `buildozer.spec` 中：

```ini
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE
```

---

## ⚠️ 常见问题

### 问题 1：构建失败

**解决方案：**
- 查看错误日志
- 确保 `main.py` 没有语法错误
- 检查 `buildozer.spec` 配置

### 问题 2：APK 无法下载

**解决方案：**
运行查找脚本：

```python
import glob
apk_files = glob.glob('**/*.apk', recursive=True)
print(apk_files)
```

### 问题 3：APK 安装后闪退

**解决方案：**
- 检查代码是否有错误
- 确保所有依赖都在 `requirements` 中
- 使用 `adb logcat` 查看日志

---

## 💡 提示

1. **保存 Colab 笔记本**：构建脚本可以保存在 Colab 中重复使用
2. **使用 GitHub**：每次修改代码后推送到 GitHub，Colab 会拉取最新代码
3. **构建缓存**：Colab 会缓存一些依赖，后续构建会更快
4. **多个应用**：可以为不同应用创建不同的 GitHub 仓库

---

## 📚 完整项目结构

```
python-calculator-android/
├── main.py                    # 你的应用代码
├── buildozer.spec            # 构建配置
├── requirements.txt          # Python 依赖
├── icon.png                  # 应用图标（可选）
├── colab_build.py           # Colab 构建脚本
└── Colab快速构建流程.md     # 本文档
```

---

## 🎯 下次构建流程

1. 修改 `main.py`
2. 提交到 GitHub：`git push`
3. 打开 Colab
4. 运行 `colab_build.py`
5. 等待并下载 APK

就这么简单！
