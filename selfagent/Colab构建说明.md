# SelfAgent - Colab 构建 Android APK 指南

## 🚀 快速开始

### 方法一：使用 Colab Notebook（推荐）

1. 打开 [Google Colab](https://colab.research.google.com/)
2. 上传 `build_colab.ipynb` 文件
3. 点击 **Runtime → Run all**
4. 等待约 15 分钟，APK 自动下载

### 方法二：手动执行

在 Colab 中新建笔记本，依次运行以下代码：

```python
# 1. 安装 Node.js
!curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
!sudo apt-get install -y nodejs

# 2. 安装 Java 和 Android SDK
!sudo apt-get install -y openjdk-17-jdk wget unzip
!mkdir -p ~/android-sdk/cmdline-tools
!wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdline-tools.zip
!unzip -q -o cmdline-tools.zip -d ~/android-sdk/cmdline-tools
!mv ~/android-sdk/cmdline-tools/cmdline-tools ~/android-sdk/cmdline-tools/latest

import os
os.environ['ANDROID_HOME'] = os.path.expanduser('~/android-sdk')
os.environ['ANDROID_SDK_ROOT'] = os.environ['ANDROID_HOME']
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'

!yes | ~/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
!~/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"

# 3. 克隆项目
!git clone https://github.com/你的用户名/你的仓库.git
%cd 你的仓库/selfagent
!npm install
!npm install -g expo-cli

# 4. 生成 Android 项目并构建
!npx expo prebuild --platform android --clean
%cd android
!chmod +x gradlew
!./gradlew assembleRelease --no-daemon

# 5. 下载 APK
from google.colab import files
files.download('app/build/outputs/apk/release/app-release.apk')
```

---

## ⚠️ 注意事项

1. **首次构建较慢**：需要下载 Android SDK，约 15-20 分钟
2. **Colab 会话限制**：免费版有 12 小时限制
3. **需要 GitHub 仓库**：先将代码推送到 GitHub

---

## 🔧 常见问题

### Q: 构建失败怎么办？
查看错误日志，常见原因：
- 网络问题：重新运行失败的单元格
- 内存不足：重启 Colab 运行时

### Q: 如何签名 APK？
在 `android/app/build.gradle` 中配置签名：
```gradle
signingConfigs {
    release {
        storeFile file('my-release-key.keystore')
        storePassword 'password'
        keyAlias 'my-key-alias'
        keyPassword 'password'
    }
}
```

### Q: 如何修改应用名称？
编辑 `app.json` 中的 `name` 和 `slug` 字段

---

## 📱 安装到手机

1. 将 APK 传输到 Android 手机
2. 打开文件管理器，点击 APK
3. 允许"未知来源"安装
4. 点击"安装"

---

## 🔄 更新流程

1. 修改代码
2. `git push` 推送到 GitHub
3. 在 Colab 重新运行构建
4. 下载新 APK 安装
