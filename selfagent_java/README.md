# SelfAgent (Java 原生版)

原生 Java/Android 实现的 SelfAgent 应用，功能与 React Native 版本相同，但构建更简单可靠。

## 功能

- 📱 站点管理 - 添加、删除、打开网站
- 🔔 WebSocket 实时消息推送
- 📅 日程管理 - 从 API 获取今日日程
- 🔔 本地通知提醒

## 在 Colab 构建

1. 打开 `build_colab.ipynb`
2. 点击 **Runtime -> Run all**
3. 等待构建完成，自动下载 APK

## 本地构建

```bash
# 需要 Java 17 和 Android SDK
./gradlew assembleRelease
```

APK 输出位置: `app/build/outputs/apk/release/`

## 项目结构

```
selfagent_java/
├── app/
│   ├── src/main/
│   │   ├── java/com/selfagent/app/
│   │   │   ├── MainActivity.java      # 主界面
│   │   │   ├── WebViewActivity.java   # WebView 页面
│   │   │   ├── SiteAdapter.java       # 站点列表适配器
│   │   │   ├── NotificationAdapter.java
│   │   │   └── ScheduleDialog.java    # 日程弹窗
│   │   ├── res/
│   │   │   ├── layout/                # 布局文件
│   │   │   ├── drawable/              # 图标和背景
│   │   │   └── values/                # 样式和颜色
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle
├── settings.gradle
└── build_colab.ipynb                  # Colab 构建脚本
```

## 优势

相比 React Native 版本:
- ✅ 无需 JS Bundle，不会出现 "Unable to load script" 错误
- ✅ 构建更快，APK 更小
- ✅ 原生性能，更流畅
- ✅ 调试更简单
