"""
通过记录光标位置来输入文本
适用于 Electron/Chrome 应用（如 Kiro）
"""

import win32gui
import win32api
import win32con
import time
import json
import os


POSITIONS_FILE = "input_positions.json"


def save_position(name, x, y):
    """保存光标位置"""
    positions = {}
    
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
            positions = json.load(f)
    
    positions[name] = {"x": x, "y": y}
    
    with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(positions, f, indent=2, ensure_ascii=False)
    
    print(f"💾 已保存位置 '{name}': ({x}, {y})")


def load_position(name):
    """加载保存的位置"""
    if not os.path.exists(POSITIONS_FILE):
        return None
    
    with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
        positions = json.load(f)
    
    return positions.get(name)


def list_positions():
    """列出所有保存的位置"""
    if not os.path.exists(POSITIONS_FILE):
        print("📋 没有保存的位置")
        return
    
    with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
        positions = json.load(f)
    
    print(f"\n📋 已保存的位置 (共 {len(positions)} 个):")
    for name, pos in positions.items():
        print(f"   {name}: ({pos['x']}, {pos['y']})")


def record_position(name):
    """记录当前光标位置"""
    print(f"\n📍 记录位置: {name}")
    print("⏰ 3 秒后记录，请将光标移到目标位置...")
    
    for i in range(3, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print()
    
    x, y = win32gui.GetCursorPos()
    save_position(name, x, y)
    
    print(f"✅ 位置已记录: ({x}, {y})")
    return x, y


def click_position(x, y):
    """点击指定位置"""
    print(f"🖱️  点击位置: ({x}, {y})")
    
    # 移动鼠标
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    
    # 点击
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.3)
    
    print("✅ 已点击")


def input_text(text):
    """输入文本"""
    print(f"⌨️  输入文本: {text}")
    
    # 使用剪贴板
    import win32clipboard
    
    try:
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
    except Exception as e:
        print(f"⚠️ 剪贴板失败: {e}")
        print("   使用逐字符输入...")
        
        for char in text:
            vk = win32api.VkKeyScan(char)
            if vk != -1:
                win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 已输入")


def press_enter():
    """按回车"""
    print("⏎  按回车...")
    time.sleep(0.2)
    
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("✅ 已按回车")


def input_at_position(name, text, press_enter_key=True):
    """在指定位置输入文本"""
    
    print("=" * 60)
    print(f"在位置 '{name}' 输入文本")
    print("=" * 60)
    
    # 加载位置
    pos = load_position(name)
    
    if not pos:
        print(f"❌ 未找到位置 '{name}'")
        print("💡 请先使用 record 命令记录位置")
        return False
    
    x, y = pos['x'], pos['y']
    
    print(f"\n📍 目标位置: ({x}, {y})")
    print(f"📝 输入文本: {text}")
    print()
    
    # 点击位置
    click_position(x, y)
    
    # 输入文本
    input_text(text)
    
    # 按回车
    if press_enter_key:
        press_enter()
    
    print("\n" + "=" * 60)
    print("✨ 完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("基于位置的文本输入工具")
    print("=" * 60)
    print("\n💡 使用方法:")
    print("   1. 记录位置: python input_by_position.py record <名称>")
    print("   2. 输入文本: python input_by_position.py input <名称> <文本>")
    print("   3. 列出位置: python input_by_position.py list")
    print()
    
    if len(sys.argv) < 2:
        print("❌ 缺少参数")
        print("\n示例:")
        print("   python input_by_position.py record chat")
        print("   python input_by_position.py input chat 继续")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "record":
        # 记录位置
        if len(sys.argv) < 3:
            name = "default"
        else:
            name = sys.argv[2]
        
        record_position(name)
    
    elif command == "input":
        # 输入文本
        if len(sys.argv) < 3:
            print("❌ 缺少位置名称")
            sys.exit(1)
        
        name = sys.argv[2]
        text = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "继续"
        
        input_at_position(name, text)
    
    elif command == "list":
        # 列出位置
        list_positions()
    
    else:
        print(f"❌ 未知命令: {command}")
        print("   可用命令: record, input, list")
