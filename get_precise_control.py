"""
精确获取光标位置的控件
使用 UI Automation 获取更深层的控件信息
"""

import win32gui
import win32api
import win32con
import time
import ctypes
from ctypes import wintypes


def get_control_at_cursor():
    """获取光标位置的精确控件信息"""
    
    print("⏰ 3 秒倒计时，请将光标放在目标输入框...")
    for i in range(3, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print("\n")
    
    # 获取光标位置
    cursor_pos = win32gui.GetCursorPos()
    print(f"🖱️  光标位置: {cursor_pos}")
    
    # 方法1：使用 WindowFromPoint 获取最顶层控件
    hwnd = win32gui.WindowFromPoint(cursor_pos)
    
    if hwnd:
        class_name = win32gui.GetClassName(hwnd)
        text = win32gui.GetWindowText(hwnd)
        
        print(f"\n✅ 光标位置的控件:")
        print(f"   句柄: {hwnd}")
        print(f"   类名: {class_name}")
        print(f"   文本: {text}")
        
        # 获取控件的矩形区域
        rect = win32gui.GetWindowRect(hwnd)
        print(f"   位置: ({rect[0]}, {rect[1]}) - ({rect[2]}, {rect[3]})")
        print(f"   大小: {rect[2]-rect[0]} x {rect[3]-rect[1]}")
        
        # 获取父窗口链
        print(f"\n📊 父窗口链:")
        current = hwnd
        level = 0
        while current:
            try:
                parent = win32gui.GetParent(current)
                if parent:
                    parent_class = win32gui.GetClassName(parent)
                    parent_text = win32gui.GetWindowText(parent)
                    print(f"   [{level}] 句柄: {parent:10d} 类名: {parent_class:30s} 文本: {parent_text[:40]}")
                    current = parent
                    level += 1
                else:
                    break
            except:
                break
        
        return hwnd, cursor_pos
    
    return None, cursor_pos


def try_uiautomation():
    """尝试使用 UI Automation 获取更详细信息"""
    try:
        import comtypes.client
        
        print("\n🔍 尝试使用 UI Automation...")
        
        # 初始化 UI Automation
        UIAutomationClient = comtypes.client.GetModule('UIAutomationCore.dll')
        automation = comtypes.client.CreateObject(
            '{ff48dba4-60ef-4201-aa87-54103eef594e}',
            interface=UIAutomationClient.IUIAutomation
        )
        
        # 获取光标位置
        cursor_pos = win32gui.GetCursorPos()
        
        # 从点获取元素
        element = automation.ElementFromPoint(
            comtypes.client.CreateObject(
                '{00000000-0000-0000-0000-000000000000}',
                interface=UIAutomationClient.tagPOINT
            )
        )
        
        if element:
            name = element.CurrentName
            control_type = element.CurrentControlType
            class_name = element.CurrentClassName
            
            print(f"✅ UI Automation 元素:")
            print(f"   名称: {name}")
            print(f"   控件类型: {control_type}")
            print(f"   类名: {class_name}")
            
            return element
    
    except Exception as e:
        print(f"⚠️ UI Automation 不可用: {e}")
        print("   (这是正常的，不影响基本功能)")
    
    return None


def save_control_info(hwnd, cursor_pos):
    """保存控件信息到文件"""
    
    filename = "control_info.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("控件信息\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"句柄: {hwnd}\n")
        f.write(f"光标位置: {cursor_pos}\n")
        f.write(f"类名: {win32gui.GetClassName(hwnd)}\n")
        f.write(f"文本: {win32gui.GetWindowText(hwnd)}\n")
        
        rect = win32gui.GetWindowRect(hwnd)
        f.write(f"位置: ({rect[0]}, {rect[1]}) - ({rect[2]}, {rect[3]})\n")
        f.write(f"大小: {rect[2]-rect[0]} x {rect[3]-rect[1]}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("使用方法:\n")
        f.write("=" * 60 + "\n")
        f.write(f"python input_by_handle.py {hwnd} 你的文本\n")
        f.write("\n或者使用光标位置点击:\n")
        f.write(f"光标位置: {cursor_pos}\n")
    
    print(f"\n💾 控件信息已保存到: {filename}")


def click_at_position(x, y):
    """在指定位置点击"""
    print(f"\n🖱️  模拟点击位置: ({x}, {y})")
    
    # 移动鼠标
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    
    # 点击
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    print("✅ 已点击")


def input_at_cursor_position(text="测试"):
    """在当前光标位置输入文本"""
    
    print(f"\n⌨️  在光标位置输入: {text}")
    
    # 使用剪贴板
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    time.sleep(0.1)
    
    # Ctrl+V
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("✅ 已粘贴")
    
    # 回车
    time.sleep(0.2)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("✅ 已按回车")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("精确获取光标位置的控件")
    print("=" * 60)
    print("\n💡 说明:")
    print("   对于 Electron/Chrome 应用（如 Kiro），")
    print("   多个输入框可能共享同一个渲染控件。")
    print("   此脚本会记录光标的精确位置。")
    print()
    
    # 获取控件
    hwnd, cursor_pos = get_control_at_cursor()
    
    if hwnd:
        # 保存信息
        save_control_info(hwnd, cursor_pos)
        
        # 尝试 UI Automation
        try_uiautomation()
        
        print("\n" + "=" * 60)
        print("📋 解决方案:")
        print("=" * 60)
        print("\n由于 Kiro 使用 Chrome 渲染，建议使用以下方法:")
        print("\n方法1: 使用光标位置点击 + 键盘输入")
        print(f"   1. 点击位置: {cursor_pos}")
        print(f"   2. 然后输入文本")
        print("\n方法2: 直接在当前位置输入（推荐）")
        print("   运行: python get_precise_control.py input 你的文本")
        print("=" * 60)
        
        # 如果有参数，执行输入
        if len(sys.argv) > 1 and sys.argv[1] == "input":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "测试"
            print(f"\n🚀 输入模式: 将输入 '{text}'")
            print("⏰ 3 秒后开始，请将光标放在目标位置...")
            time.sleep(3)
            
            # 点击光标位置
            click_at_position(*cursor_pos)
            time.sleep(0.3)
            
            # 输入文本
            input_at_cursor_position(text)
    else:
        print("\n❌ 未能获取控件")
