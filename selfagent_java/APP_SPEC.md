# SelfAgent App 功能规格说明

## 概述

SelfAgent 是一个 Android 原生应用，主要功能是作为一个**站点管理器 + 实时消息推送客户端**。用户可以管理多个网站入口，通过内置 WebView 访问，同时接收服务器推送的实时消息通知。

## 核心功能

### 1. 站点管理

- **添加站点**: 用户可以添加自定义网站，输入名称和 URL
- **删除站点**: 长按站点卡片可删除
- **打开站点**: 点击站点卡片，在内置 WebView 中打开网页
- **持久化存储**: 站点列表保存在 SharedPreferences，重启后保留

默认站点:
```
名称: 主系统
URL: http://111.170.6.103:9999/
```

### 2. WebSocket 实时消息推送

- **连接地址**: `ws://111.170.6.103:9999/ws`
- **自动重连**: 断开后 5 秒自动重连
- **消息格式**: 支持 JSON 和纯文本

JSON 消息格式:
```json
{
  "title": "消息标题",
  "message": "消息内容"  // 或 "body"
}
```

收到消息后:
1. 弹出系统通知 (Notification)
2. 添加到应用内通知列表
3. 更新通知角标数量

### 3. 日程管理

- **API 地址**: `http://111.170.6.103:9999/api/daily.php`
- **功能**: 获取今日日程列表
- **展示**: 底部弹窗显示，支持刷新

日程数据格式:
```json
[
  {
    "id": "1",
    "time": "09:00",
    "title": "会议",
    "description": "项目周会"
  }
]
```

### 4. 通知面板

- 点击顶部通知图标展开/收起
- 显示所有收到的推送消息
- 支持一键清空

## 技术架构

### 服务器端点

| 功能 | 地址 | 协议 |
|------|------|------|
| 主系统 | http://111.170.6.103:9999/ | HTTP |
| WebSocket | ws://111.170.6.103:9999/ws | WebSocket |
| 日程 API | http://111.170.6.103:9999/api/daily.php | HTTP GET |

### 依赖库

- OkHttp: HTTP 请求和 WebSocket
- Gson: JSON 解析
- AndroidX: UI 组件

### 权限

- `INTERNET`: 网络访问
- `POST_NOTIFICATIONS`: 发送通知

## UI 结构

```
MainActivity (主界面)
├── Header (顶部栏)
│   ├── 标题 "SelfAgent"
│   ├── 日程按钮 → ScheduleDialog
│   └── 通知按钮 (带角标) → 通知面板
├── 通知面板 (可展开/收起)
│   ├── 消息列表
│   └── 清空按钮
├── 站点列表 (RecyclerView)
│   └── 站点卡片 (点击打开, 长按删除)
└── 添加站点按钮 → 添加弹窗

WebViewActivity (网页浏览)
├── Header
│   ├── 返回按钮
│   └── 站点名称
└── WebView
```

## 主题色

- 主色: `#667eea` (紫蓝色)
- 背景: `#f5f7fa` (浅灰)
- 角标: `#ff4757` (红色)

## 数据流

```
服务器 WebSocket ──推送消息──→ App
                              ├─→ 系统通知
                              └─→ 通知列表

用户 ──点击站点──→ WebView ──加载──→ 服务器网页

用户 ──点击日程──→ App ──HTTP GET──→ 日程 API
                        ←─JSON─┘
```

## 构建

使用 Google Colab 构建:
1. 打开 `build_colab.ipynb`
2. 运行所有单元格
3. 下载生成的 APK

## 扩展建议

如需修改或扩展功能:

1. **更换服务器地址**: 修改 `MainActivity.java` 中的常量
2. **添加新功能**: 在 `MainActivity` 中添加新的 UI 和逻辑
3. **修改 UI 样式**: 编辑 `res/layout/` 和 `res/drawable/` 中的 XML 文件
4. **添加新页面**: 创建新的 Activity 并在 AndroidManifest.xml 中注册
