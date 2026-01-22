"""
向 Kiro 编辑器输入文本
"""

import win32gui
import win32con
import win32api
import time


def input_to_kiro(text="继续"):
    """向 Kiro 窗口输入文本"""
    
    # 1. 查找 Kiro 窗口
    print("🔍 查找 Kiro 窗口...")
    
    def find_kiro_window(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Kiro" in title:
                results.append((hwnd, title))
        return True
    
    results = []
    win32gui.EnumWindows(find_kiro_window, results)
    
    if not results:
        print("❌ 未找到 Kiro 窗口")
        return False
    
    # 使用第一个找到的 Kiro 窗口
    hwnd, title = results[0]
    print(f"✅ 找到窗口: {title}")
    print(f"   句柄: {hwnd}")
    
    # 2. 激活窗口
    print("\n⚡ 激活窗口...")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    
    # 3. 查找所有 Edit 控件
    print("\n🔍 查找文本输入框...")
    
    def find_all_edits(child_hwnd, results):
        class_name = win32gui.GetClassName(child_hwnd)
        if "Edit" in class_name or "Text" in class_name:
            # 检查控件是否可见和可用
            if win32gui.IsWindowVisible(child_hwnd) and win32gui.IsWindowEnabled(child_hwnd):
                results.append((child_hwnd, class_name))
        return True
    
    edit_controls = []
    win32gui.EnumChildWindows(hwnd, find_all_edits, edit_controls)
    
    print(f"✅ 找到 {len(edit_controls)} 个文本控件")
    
    if not edit_controls:
        print("❌ 未找到文本输入框")
        print("\n💡 尝试使用键盘模拟输入...")
        
        # 方法2：直接模拟键盘输入
        time.sleep(0.5)
        for char in text:
            # 发送字符
            win32api.keybd_event(0, win32api.MapVirtualKey(ord(char), 0), 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(0, win32api.MapVirtualKey(ord(char), 0), win32con.KEYEVENTF_KEYUP, 0)
        
        print(f"✅ 已输入: {text}")
        
        # 按回车
        time.sleep(0.2)
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("✅ 已按回车")
        
        return True
    
    # 4. 尝试向每个文本控件输入
    for i, (edit_hwnd, class_name) in enumerate(edit_controls):
        print(f"\n📝 尝试控件 [{i}] (类名: {class_name}, 句柄: {edit_hwnd})")
        
        try:
            # 方法1：使用 WM_SETTEXT
            win32api.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, text)
            time.sleep(0.2)
            
            # 验证是否成功
            length = win32gui.SendMessage(edit_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                print(f"✅ 成功输入到控件 [{i}]: {text}")
                
                # 按回车
                time.sleep(0.2)
                win32api.SendMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                time.sleep(0.05)
                win32api.SendMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                print("✅ 已按回车")
                
                return True
        except Exception as e:
            print(f"   ⚠️ 失败: {e}")
            continue
    
    print("\n❌ 所有控件都无法输入")
    return False


def input_to_kiro_simple(text="继续"):
    """简化版：直接模拟键盘输入"""
    
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
    
    hwnd, title = results[0]
    print(f"✅ 找到: {title}")
    
    # 查找聊天输入框
    print("🔍 查找聊天输入框...")
    
    def find_chat_input(child_hwnd, results):
        class_name = win32gui.GetClassName(child_hwnd)
        # 查找 Chrome 渲染控件（Kiro 的聊天框）
        if "Chrome" in class_name and win32gui.IsWindowVisible(child_hwnd):
            results.append((child_hwnd, class_name))
        return True
    
    chat_controls = []
    win32gui.EnumChildWindows(hwnd, find_chat_input, chat_controls)
    
    if chat_controls:
        chat_hwnd, class_name = chat_controls[0]
        print(f"✅ 找到聊天框: {class_name} (句柄: {chat_hwnd})")
        
        # 先激活主窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        # 点击聊天框使其获得焦点
        print("🖱️  点击聊天框...")
        # 获取聊天框的位置
        rect = win32gui.GetWindowRect(chat_hwnd)
        x = (rect[0] + rect[2]) // 2
        y = (rect[1] + rect[3]) // 2
        
        # 将屏幕坐标转换为客户区坐标
        client_point = win32gui.ScreenToClient(hwnd, (x, y))
        
        # 发送鼠标点击消息
        lParam = win32api.MAKELONG(client_point[0], client_point[1])
        win32api.SendMessage(chat_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.05)
        win32api.SendMessage(chat_hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        time.sleep(0.3)
        
        print("✅ 聊天框已获得焦点")
    else:
        print("⚠️ 未找到聊天框，使用主窗口")
        # 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
    
    # 模拟键盘输入
    print(f"\n⌨️  输入文本: {text}")
    
    # 使用 Windows 剪贴板 API
    import win32clipboard
    
    try:
        # 方法1：使用剪贴板（最可靠）
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        
        # Ctrl+V 粘贴
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 已粘贴文本")
        



    except Exception as e:
        print(f"⚠️ 剪贴板方法失败: {e}")
        print("💡 使用逐字符输入...")
        
        # 方法2：逐字符输入
        for char in text:
            # 使用 VkKeyScan 获取虚拟键码
            vk = win32api.VkKeyScan(char)
            if vk != -1:
                win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 已输入文本")
    
    # 按回车
    time.sleep(0.3)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("✅ 已按回车")
    
    return True


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("向 Kiro 输入文本")
    print("=" * 60)
    
    # 获取要输入的文本
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "继续"
    
    print(f"\n📝 将要输入: {text}")
    print("\n⏰ 3 秒后开始...")
    time.sleep(3)
    
    # 尝试简化版
    success = input_to_kiro_simple(text)
    
    if not success:
        print("\n💡 尝试完整版...")
        input_to_kiro(text)
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
