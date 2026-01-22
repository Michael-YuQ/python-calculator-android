"""
自动化 Kiro 输入
1. 查找并激活 Kiro 窗口
2. 移动光标到指定位置
3. 点击并输入文本
4. 按回车发送
"""

import win32gui
import win32api
import win32con
import time


def find_and_activate_kiro():
    """查找并激活 Kiro 窗口"""
    
    print("🔍 查找 Kiro 窗口...")
    
    def find_window(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # 查找包含 "Kiro" 的窗口
            if "Kiro" in title:
                results.append((hwnd, title))
        return True
    
    results = []
    win32gui.EnumWindows(find_window, results)
    
    if not results:
        print("❌ 未找到 Kiro 窗口")
        print("💡 请确保 Kiro 已经打开")
        return None, None
    
    # 如果有多个 Kiro 窗口，显示列表
    if len(results) > 1:
        print(f"\n✅ 找到 {len(results)} 个 Kiro 窗口:")
        for i, (hwnd, title) in enumerate(results):
            print(f"   [{i}] {title}")
        
        # 使用第一个
        hwnd, title = results[0]
        print(f"\n使用第一个窗口: {title}")
    else:
        hwnd, title = results[0]
        print(f"✅ 找到窗口: {title}")
    
    print(f"   句柄: {hwnd}")
    
    # 激活窗口
    print("\n⚡ 激活窗口...")
    
    try:
        # 如果窗口最小化，先恢复
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
        
        # 将窗口置于前台
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        print("✅ 窗口已激活")
        
        return hwnd, title
        
    except Exception as e:
        print(f"⚠️ 激活窗口失败: {e}")
        print("   尝试使用 Alt+Tab 切换...")
        
        # 尝试使用 Alt+Tab
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt down
        win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)   # Tab down
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)  # Tab up
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt up
        time.sleep(0.5)
        
        return hwnd, title


def move_and_click(x, y):
    """移动鼠标到指定位置并点击"""
    
    print(f"\n🖱️  移动到位置: ({x}, {y})")
    
    # 移动鼠标
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    
    print("✅ 鼠标已移动")
    
    # 点击
    print("🖱️  点击...")
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.3)
    
    print("✅ 已点击")


def input_text(text):
    """输入文本"""
    
    print(f"\n⌨️  输入文本: {text}")
    
    try:
        # 使用剪贴板粘贴
        import win32clipboard
        
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
        
        print("✅ 文本已粘贴")
        
    except Exception as e:
        print(f"⚠️ 剪贴板方法失败: {e}")
        print("   使用逐字符输入...")
        
        # 逐字符输入
        for char in text:
            vk = win32api.VkKeyScan(char)
            if vk != -1:
                # 检查是否需要按 Shift
                if vk & 0x100:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                
                win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                if vk & 0x100:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 文本已输入")


def press_enter():
    """按回车"""
    
    print("\n⏎  按回车发送...")
    time.sleep(0.3)
    
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("✅ 已按回车")


def auto_input_to_kiro(x=1228, y=720, text="继续", wait_time=0):
    """
    自动化输入到 Kiro
    
    参数:
        x: X 坐标
        y: Y 坐标
        text: 要输入的文本
        wait_time: 开始前等待时间（秒）
    """
    
    print("=" * 60)
    print("Kiro 自动化输入")
    print("=" * 60)
    
    print(f"\n📍 目标位置: ({x}, {y})")
    print(f"📝 输入文本: {text}")
    
    if wait_time > 0:
        print(f"\n⏰ {wait_time} 秒后开始...")
        time.sleep(wait_time)
    
    print()
    
    # 步骤1: 查找并激活 Kiro 窗口
    print("[1/4] 查找并激活 Kiro 窗口")
    print("-" * 60)
    hwnd, title = find_and_activate_kiro()
    
    if not hwnd:
        return False
    
    # 步骤2: 移动鼠标并点击
    print("\n[2/4] 移动鼠标并点击目标位置")
    print("-" * 60)
    move_and_click(x, y)
    
    # 步骤3: 输入文本
    print("\n[3/4] 输入文本")
    print("-" * 60)
    input_text(text)
    
    # 步骤4: 按回车
    print("\n[4/4] 按回车发送")
    print("-" * 60)
    press_enter()
    
    print("\n" + "=" * 60)
    print("✨ 完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import sys
    
    # 默认参数
    x = 1228
    y = 720
    text = "继续"
    wait_time = 3
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        # 检查是否有 --now 参数（立即执行）
        if "--now" in sys.argv:
            wait_time = 0
            sys.argv.remove("--now")
        
        # 解析位置和文本
        if len(sys.argv) > 1:
            if sys.argv[1].isdigit():
                # 格式: python kiro_auto_input.py 1228 720 继续
                x = int(sys.argv[1])
                if len(sys.argv) > 2 and sys.argv[2].isdigit():
                    y = int(sys.argv[2])
                    text = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "继续"
                else:
                    text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "继续"
            else:
                # 格式: python kiro_auto_input.py 继续
                text = " ".join(sys.argv[1:])
    
    print("\n" + "=" * 60)
    print("配置信息")
    print("=" * 60)
    print(f"目标位置: ({x}, {y})")
    print(f"输入文本: {text}")
    print(f"等待时间: {wait_time} 秒")
    print("=" * 60)
    
    if wait_time > 0:
        print(f"\n⏰ {wait_time} 秒后开始...")
        print("💡 提示：脚本会自动激活 Kiro 窗口\n")
        time.sleep(wait_time)
    
    auto_input_to_kiro(x, y, text, wait_time=0)
