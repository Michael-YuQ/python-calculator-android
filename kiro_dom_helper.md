# Kiro DOM 结构检查指南

## 方法一：使用开发者工具（推荐）

### 1. 打开开发者工具
在 Kiro 中按：`Ctrl + Shift + I`

### 2. 使用 Elements 面板
- 点击左上角的"选择元素"工具（箭头图标）
- 点击页面上的任何元素
- 在 Elements 面板中查看 HTML 结构

### 3. 在 Console 中查询元素

```javascript
// 查找聊天输入框
document.querySelector('textarea')
document.querySelector('input[type="text"]')
document.querySelector('[contenteditable="true"]')

// 查找所有输入框
document.querySelectorAll('input, textarea, [contenteditable]')

// 获取元素位置
const element = document.querySelector('textarea');
const rect = element.getBoundingClientRect();
console.log('位置:', rect.x, rect.y);
console.log('大小:', rect.width, rect.height);

// 获取元素的所有属性
const element = document.querySelector('textarea');
console.log('ID:', element.id);
console.log('Class:', element.className);
console.log('Name:', element.name);
console.log('Placeholder:', element.placeholder);

// 模拟输入
const input = document.querySelector('textarea');
input.value = '继续';
input.dispatchEvent(new Event('input', { bubbles: true }));

// 模拟按回车
const event = new KeyboardEvent('keydown', {
    key: 'Enter',
    code: 'Enter',
    keyCode: 13,
    bubbles: true
});
input.dispatchEvent(event);
```

---

## 方法二：使用 Python 检查窗口结构

### 1. 检查 Win32 窗口层级
```bash
python inspect_window.py
```

### 2. 检查当前窗口
```bash
python inspect_window.py current
```

---

## 方法三：使用 Chrome DevTools Protocol

### 1. 启动 Kiro 时添加调试参数
```bash
kiro.exe --remote-debugging-port=9222
```

### 2. 访问调试界面
打开浏览器访问：`http://localhost:9222`

### 3. 使用 Python 连接
```python
import requests
import json

# 获取所有页面
response = requests.get('http://localhost:9222/json')
pages = response.json()

for page in pages:
    print(f"标题: {page['title']}")
    print(f"URL: {page['url']}")
    print(f"WebSocket: {page['webSocketDebuggerUrl']}")
```

---

## 常见的 Electron 应用 DOM 结构

### 聊天输入框可能的选择器：

```javascript
// 1. Textarea
document.querySelector('textarea')
document.querySelector('textarea[placeholder*="输入"]')
document.querySelector('textarea[placeholder*="消息"]')

// 2. ContentEditable Div
document.querySelector('[contenteditable="true"]')
document.querySelector('div[contenteditable="true"]')

// 3. Input
document.querySelector('input[type="text"]')
document.querySelector('input.chat-input')

// 4. 特定 Class 或 ID
document.querySelector('#chat-input')
document.querySelector('.message-input')
document.querySelector('[data-testid="chat-input"]')
```

### 获取所有可输入元素：

```javascript
// 查找所有可能的输入元素
const inputs = document.querySelectorAll(`
    input[type="text"],
    input[type="search"],
    textarea,
    [contenteditable="true"]
`);

inputs.forEach((input, index) => {
    const rect = input.getBoundingClientRect();
    console.log(`[${index}]`, {
        tag: input.tagName,
        type: input.type,
        id: input.id,
        class: input.className,
        placeholder: input.placeholder,
        position: { x: rect.x, y: rect.y },
        size: { width: rect.width, height: rect.height }
    });
});
```

---

## 方法四：使用 Accessibility API

### Python 代码：

```python
import win32gui
import win32con
from comtypes.client import CreateObject, GetModule

# 加载 UI Automation
GetModule('UIAutomationCore.dll')
import comtypes.gen.UIAutomationClient as UIA

automation = CreateObject(
    '{ff48dba4-60ef-4201-aa87-54103eef594e}',
    interface=UIA.IUIAutomation
)

# 获取窗口元素
hwnd = win32gui.FindWindow(None, "Kiro")
element = automation.ElementFromHandle(hwnd)

# 查找所有 Edit 控件
condition = automation.CreatePropertyCondition(
    UIA.UIA_ControlTypePropertyId,
    UIA.UIA_EditControlTypeId
)

edits = element.FindAll(UIA.TreeScope_Descendants, condition)

for i in range(edits.Length):
    edit = edits.GetElement(i)
    print(f"[{i}] {edit.CurrentName}")
    print(f"    AutomationId: {edit.CurrentAutomationId}")
    print(f"    ClassName: {edit.CurrentClassName}")
```

---

## 实用技巧

### 1. 监听元素变化
```javascript
// 监听 DOM 变化
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        console.log('DOM 变化:', mutation);
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true
});
```

### 2. 查找元素的唯一标识
```javascript
function getUniqueSelector(element) {
    if (element.id) return `#${element.id}`;
    
    let path = [];
    while (element.parentElement) {
        let selector = element.tagName.toLowerCase();
        
        if (element.className) {
            selector += '.' + element.className.split(' ').join('.');
        }
        
        path.unshift(selector);
        element = element.parentElement;
    }
    
    return path.join(' > ');
}

// 使用
const input = document.querySelector('textarea');
console.log('选择器:', getUniqueSelector(input));
```

### 3. 获取元素的绝对位置
```javascript
function getAbsolutePosition(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + window.screenX,
        y: rect.top + window.screenY,
        width: rect.width,
        height: rect.height
    };
}
```

---

## 总结

**最简单的方法：**
1. 按 `Ctrl+Shift+I` 打开开发者工具
2. 使用选择工具点击输入框
3. 在 Console 中获取元素信息
4. 记录元素的选择器或位置

**最可靠的方法：**
使用坐标点击 + 键盘输入（已实现在 `kiro_auto_input.py` 中）
