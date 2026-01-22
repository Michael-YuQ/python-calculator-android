"""
检查窗口结构
支持：
1. Win32 窗口层级结构
2. UI Automation 树结构
3. Chrome DevTools Protocol (CDP) - 用于 Electron 应用
"""

import win32gui
import win32api
import win32con
import time
import json


def get_window_tree(hwnd, level=0, max_level=5):
    """获取窗口的层级结构"""
    
    if level > max_level:
        return None
    
    try:
        class_name = win32gui.GetClassName(hwnd)
        text = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        enabled = win32gui.IsWindowEnabled(hwnd)
        
        node = {
            "hwnd": hwnd,
            "class": class_name,
            "text": text,
            "rect": rect,
            "visible": visible,
            "enabled": enabled,
            "children": []
        }
        
        # 获取子窗口
        def enum_child(child_hwnd, results):
            child_node = get_window_tree(child_hwnd, level + 1, max_level)
            if child_node:
                results.append(child_node)
            return True
        
        children = []
        win32gui.EnumChildWindows(hwnd, enum_child, children)
        node["children"] = children
        
        return node
        
    except Exception as e:
        return None


def print_window_tree(node, level=0, show_invisible=False):
    """打印窗口树"""
    
    if not node:
        return
    
    if not show_invisible and not node["visible"]:
        return
    
    indent = "  " * level
    
    # 显示信息
    info = f"{indent}[{level}] "
    info += f"句柄:{node['hwnd']:10d} "
    info += f"类:{node['class']:30s} "
    
    if node['text']:
        info += f"文本:{node['text'][:40]}"
    
    if not node['visible']:
        info += " (隐藏)"
    if not node['enabled']:
        info += " (禁用)"
    
    print(info)
    
    # 递归打印子节点
    for child in node["children"]:
        print_window_tree(child, level + 1, show_invisible)


def save_window_tree(node, filename="window_tree.json"):
    """保存窗口树到 JSON 文件"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(node, f, indent=2, ensure_ascii=False)
    
    print(f"💾 窗口树已保存到: {filename}")


def inspect_with_uiautomation():
    """使用 UI Automation 检查窗口"""
    
    try:
        from comtypes.client import CreateObject, GetModule
        
        print("\n🔍 使用 UI Automation 检查...")
        
        # 加载 UI Automation
        GetModule('UIAutomationCore.dll')
        import comtypes.gen.UIAutomationClient as UIA
        
        automation = CreateObject(
            '{ff48dba4-60ef-4201-aa87-54103eef594e}',
            interface=UIA.IUIAutomation
        )
        
        # 获取前台窗口
        hwnd = win32gui.GetForegroundWindow()
        element = automation.ElementFromHandle(hwnd)
        
        if element:
            print(f"✅ UI Automation 元素:")
            print(f"   名称: {element.CurrentName}")
            print(f"   类名: {element.CurrentClassName}")
            print(f"   控件类型: {element.CurrentControlType}")
            print(f"   自动化ID: {element.CurrentAutomationId}")
            
            # 遍历子元素
            print(f"\n📋 子元素:")
            walker = automation.ControlViewWalker
            child = walker.GetFirstChildElement(element)
            
            count = 0
            while child and count < 20:
                try:
                    name = child.CurrentName
                    class_name = child.CurrentClassName
                    control_type = child.CurrentControlType
                    
                    print(f"   [{count}] {name[:40]:40s} 类:{class_name:20s} 类型:{control_type}")
                    
                    child = walker.GetNextSiblingElement(child)
                    count += 1
                except:
                    break
            
            return True
    
    except Exception as e:
        print(f"⚠️ UI Automation 不可用: {e}")
        return False


def inspect_chrome_devtools():
    """
    检查 Chrome/Electron 应用的 DOM 结构
    需要应用开启了 DevTools Protocol
    """
    
    print("\n🔍 Chrome DevTools Protocol 检查...")
    print("💡 提示：需要 Electron 应用开启远程调试")
    print("   启动参数: --remote-debugging-port=9222")
    
    try:
        import requests
        
        # 尝试连接到 Chrome DevTools
        response = requests.get('http://localhost:9222/json', timeout=2)
        
        if response.status_code == 200:
            pages = response.json()
            
            print(f"\n✅ 找到 {len(pages)} 个页面:")
            for i, page in enumerate(pages):
                print(f"\n   [{i}] {page.get('title', 'Untitled')}")
                print(f"       URL: {page.get('url', 'N/A')}")
                print(f"       WebSocket: {page.get('webSocketDebuggerUrl', 'N/A')}")
            
            return True
        else:
            print("❌ 无法连接到 DevTools")
            return False
    
    except Exception as e:
        print(f"❌ DevTools 不可用: {e}")
        print("\n💡 如果是 Electron 应用，可以尝试:")
        print("   1. 在应用中按 Ctrl+Shift+I 打开开发者工具")
        print("   2. 使用开发者工具的 Elements 面板查看 DOM")
        return False


def find_kiro_and_inspect():
    """查找 Kiro 窗口并检查"""
    
    print("=" * 60)
    print("Kiro 窗口结构检查")
    print("=" * 60)
    
    # 查找 Kiro 窗口
    print("\n🔍 查找 Kiro 窗口...")
    
    def find_kiro(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Kiro" in title:
                results.append((hwnd, title))
        return True
    
    results = []
    win32gui.EnumWindows(find_kiro, results)
    
    if not results:
        print("❌ 未找到 Kiro 窗口")
        return
    
    hwnd, title = results[0]
    print(f"✅ 找到窗口: {title}")
    print(f"   句柄: {hwnd}")
    
    # 方法1: Win32 窗口树
    print("\n" + "=" * 60)
    print("方法1: Win32 窗口层级结构")
    print("=" * 60)
    
    tree = get_window_tree(hwnd, max_level=3)
    print_window_tree(tree)
    
    # 保存到文件
    save_window_tree(tree, "kiro_window_tree.json")
    
    # 方法2: UI Automation
    print("\n" + "=" * 60)
    print("方法2: UI Automation")
    print("=" * 60)
    
    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    inspect_with_uiautomation()
    
    # 方法3: Chrome DevTools
    print("\n" + "=" * 60)
    print("方法3: Chrome DevTools Protocol")
    print("=" * 60)
    
    inspect_chrome_devtools()
    
    # 提示
    print("\n" + "=" * 60)
    print("💡 查看 DOM 结构的最佳方法:")
    print("=" * 60)
    print("\n1. 在 Kiro 中按 Ctrl+Shift+I 打开开发者工具")
    print("2. 点击 Elements 标签")
    print("3. 使用选择工具（左上角箭头）点击元素")
    print("4. 在 Elements 面板中查看 HTML 结构")
    print("\n5. 在 Console 中可以使用 JavaScript:")
    print("   document.querySelector('选择器')")
    print("   document.querySelectorAll('选择器')")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "current":
        # 检查当前前台窗口
        print("⏰ 3 秒后检查当前窗口...")
        time.sleep(3)
        
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        
        print(f"\n当前窗口: {title}")
        print(f"句柄: {hwnd}")
        
        tree = get_window_tree(hwnd, max_level=3)
        print_window_tree(tree)
        save_window_tree(tree, "current_window_tree.json")
    else:
        # 检查 Kiro 窗口
        find_kiro_and_inspect()
