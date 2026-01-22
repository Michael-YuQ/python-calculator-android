"""
向 Kiro 聊天框输入文本 - 改进版
自动查找并设置焦点到聊天输入框
"""

import win32gui
import win32con
import win32api
import time


def find_kiro_window():
    """查找 Kiro 窗口"""
    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Kiro" in title:
                results.append((hwnd, title))
        return True
    
    results = []
    win32gui.EnumWindows(callback, results)
    return results[0] if results else (None, None)


def find_chat_input(main_hwnd):
    """查找聊天输入框"""
    def callback(child_hwnd, results):
        class_name = win32gui.GetClassName(child_hwnd)
        # Kiro 使用 Chrome 渲染引擎
        if "Chrome" in class_name and win32gui.IsWindowVisible(child_hwnd):
            results.append((child_hwnd, class_name))
        return True
    
    results = []
    win32gui.EnumChildWindows(main_hwnd, callback, results)
    return results[0] if results else (None, None)


def set_focus_to_control(main_hwnd, control_hwnd):
    """设置焦点到指定控件"""
    try:
        # 方法1：激活主窗口
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.2)
        
        # 方法2：发送 WM_SETFOCUS 消息
        win32api.SendMessage(control_hwnd, win32con.WM_SETFOCUS, 0, 0)
        time.sleep(0.1)
        
        # 方法3：模拟鼠标点击
        rect = win32gui.GetWindowRect(control_hwnd)
        # 计算控件中心点
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        # 移动鼠标到控件中心
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.1)
        
        # 模拟鼠标点击
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.2)
        
        return True
    except Exception as e:
        print(f"⚠️ 设置焦点失败: {e}")
        return False


def input_text_to_kiro(text="继续"):
    """向 Kiro 输入文本"""
    
    print("=" * 60)
    print("向 Kiro 聊天框输入文本")
    print("=" * 60)
    
    # 1. 查找 Kiro 窗口
    print("\n[1/4] 查找 Kiro 窗口...")
    main_hwnd, title = find_kiro_window()
    
    if not main_hwnd:
        print("❌ 未找到 Kiro 窗口")
        return False
    
    print(f"✅ 找到: {title}")
    print(f"   主窗口句柄: {main_hwnd}")
    
    # 2. 查找聊天输入框
    print("\n[2/4] 查找聊天输入框...")
    chat_hwnd, class_name = find_chat_input(main_hwnd)
    
    if not chat_hwnd:
        print("⚠️ 未找到聊天输入框，使用键盘直接输入")
        chat_hwnd = None
    else:
        print(f"✅ 找到聊天框: {class_name}")
        print(f"   聊天框句柄: {chat_hwnd}")
    
    # 3. 设置焦点
    print("\n[3/4] 设置焦点到聊天框...")
    
    if chat_hwnd:
        if set_focus_to_control(main_hwnd, chat_hwnd):
            print("✅ 聊天框已获得焦点")
        else:
            print("⚠️ 无法设置焦点，继续尝试输入")
    else:
        # 只激活主窗口
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.5)
        print("✅ 主窗口已激活")
    
    # 4. 输入文本
    print(f"\n[4/4] 输入文本: {text}")
    
    try:
        # 使用剪贴板粘贴（最可靠）
        import win32clipboard
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        
        print("   使用 Ctrl+V 粘贴...")
        
        # Ctrl+V 粘贴
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 文本已粘贴")
        
    except Exception as e:
        print(f"⚠️ 剪贴板方法失败: {e}")
        print("   使用逐字符输入...")
        
        # 逐字符输入
        for char in text:
            vk = win32api.VkKeyScan(char)
            if vk != -1:
                win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 文本已输入")
    
    # 5. 按回车
    print("\n[5/5] 按回车发送...")
    time.sleep(0.3)
    
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("✅ 已按回车")
    
    print("\n" + "=" * 60)
    print("✨ 完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import sys
    
    # 获取要输入的文本
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "继续"
    
    print(f"\n📝 将要输入: {text}")
    print("⏰ 3 秒后开始...")
    print("💡 提示：请确保 Kiro 窗口可见\n")
    
    time.sleep(3)
    
    input_text_to_kiro(text)
