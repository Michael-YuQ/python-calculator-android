# SelfAgent - 个人助手 App

一个美观的移动端应用，支持管理多个网页系统入口，并提供日程提醒功能。

## 功能特性

- 📱 **多站点管理**: 可自由添加/删除网页系统链接
- 🔔 **消息提醒**: 顶部导航栏下拉通知面板
- 📅 **日程管理**: 
  - 每天早上8点推送当日日程
  - 日程开始前15分钟提醒
  - 从 API 获取日程数据
- 🌐 **内置浏览器**: WebView 打开各个系统

## 快速开始

### 1. 安装依赖

```bash
cd selfagent
npm install
```

### 2. 启动开发服务器

```bash
npm start
```

### 3. 运行应用

- 扫描二维码在 Expo Go 中打开
- 或按 `a` 在 Android 模拟器中运行
- 或按 `i` 在 iOS 模拟器中运行

## API 配置

日程 API 地址: `http://111.170.6.103:9999/api/daily.php`

### API 返回格式示例

```json
[
  {
    "id": 1,
    "time": "09:00",
    "title": "晨会",
    "description": "部门例会"
  },
  {
    "id": 2,
    "time": "14:00",
    "title": "项目评审",
    "description": "Q1项目进度汇报"
  }
]
```

## 使用说明

### 添加站点
点击"添加新站点"卡片，输入名称和网址即可

### 删除站点
长按站点卡片，确认后删除

### 查看日程
点击顶部日历图标，查看今日日程

### 查看通知
点击顶部铃铛图标，展开通知面板

## 构建发布

```bash
# 构建 Android APK
npx expo build:android

# 构建 iOS
npx expo build:ios
```

## 技术栈

- React Native + Expo
- expo-notifications (本地通知)
- react-native-webview
- @react-native-async-storage/async-storage
