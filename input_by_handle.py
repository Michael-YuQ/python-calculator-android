"""
直接通过句柄向文本框输入文本
"""

import win32gui
import win32con
import win32api
import time


def input_to_handle(hwnd, text):
    """
    直接向指定句柄的控件输入文本
    
    参数:
        hwnd: 控件句柄（整数）
        text: 要输入的文本
    """
    print(f"🎯 目标句柄: {hwnd}")
    print(f"📝 输入文本: {text}")
    
    try:
        # 获取控件信息
        class_name = win32gui.GetClassName(hwnd)
        print(f"   控件类名: {class_name}")
        
        # 检查控件是否存在
        if not win32gui.IsWindow(hwnd):
            print("❌ 句柄无效或窗口已关闭")
            return False
        
        # 获取父窗口
        parent_hwnd = win32gui.GetParent(hwnd)
        if parent_hwnd:
            parent_title = win32gui.GetWindowText(parent_hwnd)
            print(f"   父窗口: {parent_title}")
            
            # 激活父窗口
            win32gui.SetForegroundWindow(parent_hwnd)
            time.sleep(0.3)
        
        # 方法1：使用 WM_SETTEXT
        print("\n💡 方法1: WM_SETTEXT")
        win32api.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)
        time.sleep(0.2)
        
        # 验证是否成功
        length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
        if length > 0:
            print(f"✅ 成功！文本长度: {length}")
        else:
            print("⚠️ 方法1失败，尝试方法2...")
            
            # 方法2：逐字符发送 WM_CHAR
            print("\n💡 方法2: WM_CHAR")
            for char in text:
                win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
                time.sleep(0.01)
            print("✅ 已发送字符")
        
        # 发送回车键
        print("\n⏎ 发送回车...")
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        time.sleep(0.05)
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
        print("✅ 已按回车")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def input_to_kiro_chat(text="继续"):
    """
    向 Kiro 聊天框输入文本（自动查找）
    """
    print("🔍 查找 Kiro 窗口...")
    
    # 查找 Kiro 窗口
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
        return False
    
    main_hwnd, title = results[0]
    print(f"✅ 找到: {title}")
    print(f"   主窗口句柄: {main_hwnd}")
    
    # 查找所有子控件
    print("\n🔍 查找文本输入框...")
    
    def find_controls(child_hwnd, results):
        class_name = win32gui.GetClassName(child_hwnd)
        control_text = win32gui.GetWindowText(child_hwnd)
        
        # 查找可能的输入框
        if win32gui.IsWindowVisible(child_hwnd) and win32gui.IsWindowEnabled(child_hwnd):
            # 常见的输入框类名
            if any(keyword in class_name for keyword in ['Edit', 'Text', 'Input', 'Chrome']):
                results.append((child_hwnd, class_name, control_text))
        
        return True
    
    controls = []
    win32gui.EnumChildWindows(main_hwnd, find_controls, controls)
    
    print(f"✅ 找到 {len(controls)} 个可能的输入控件:")
    for i, (hwnd, class_name, text) in enumerate(controls):
        print(f"   [{i}] 句柄: {hwnd:10d} 类名: {class_name:30s} 文本: {text[:50]}")
    
    if not controls:
        print("\n❌ 未找到输入控件")
        print("💡 尝试使用键盘模拟...")
        
        # 激活窗口并模拟键盘输入
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.5)
        
        # 使用剪贴板粘贴
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
        
        print("✅ 已粘贴文本")
        
        # 回车
        time.sleep(0.3)
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("✅ 已按回车")
        
        return True
    
    # 尝试向每个控件输入
    print(f"\n📝 尝试输入文本: {text}")
    
    for i, (hwnd, class_name, _) in enumerate(controls):
        print(f"\n尝试控件 [{i}]...")
        if input_to_handle(hwnd, text):  # 使用参数 text，不是控件文本
            return True
    
    print("\n❌ 所有控件都失败")
    return False


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("向 Kiro 输入文本")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            # 直接使用句柄
            hwnd = int(sys.argv[1])
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "继续"
            
            print(f"\n📌 使用指定句柄: {hwnd}")
            print(f"📝 输入文本: {text}")
            print("\n⏰ 3 秒后开始...")
            time.sleep(3)
            
            input_to_handle(hwnd, text)
        else:
            # 使用文本作为输入
            text = " ".join(sys.argv[1:])
            
            print(f"\n📝 输入文本: {text}")
            print("\n⏰ 3 秒后开始...")
            time.sleep(3)
            
            input_to_kiro_chat(text)
    else:
        # 默认输入"继续"
        text = "继续"
        
        print(f"\n📝 输入文本: {text}")
        print("\n⏰ 3 秒后开始...")
        time.sleep(3)
        
        input_to_kiro_chat(text)
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
