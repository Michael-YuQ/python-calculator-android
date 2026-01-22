"""
向 Kiro 聊天框输入"继续"并按回车
直接使用坐标 (1228, 720)
"""

import win32gui
import win32api
import win32con
import time


def input_continue_at_position(x=1228, y=720, text="继续"):
    """
    在指定位置输入文本并按回车
    
    参数:
        x: X 坐标
        y: Y 坐标
        text: 要输入的文本
    """
    
    print("=" * 60)
    print("向 Kiro 输入文本")
    print("=" * 60)
    
    print(f"\n📍 目标位置: ({x}, {y})")
    print(f"📝 输入文本: {text}")
    print()
    
    # 步骤1: 移动鼠标到目标位置
    print("[1/4] 移动鼠标到目标位置...")
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    print("✅ 鼠标已移动")
    
    # 步骤2: 点击目标位置
    print("\n[2/4] 点击目标位置...")
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.3)
    print("✅ 已点击")
    
    # 步骤3: 输入文本
    print(f"\n[3/4] 输入文本: {text}")
    
    try:
        # 使用剪贴板粘贴（最可靠）
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
                if vk & 0x100:  # 需要 Shift
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                
                win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                if vk & 0x100:  # 释放 Shift
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("✅ 文本已输入")
    
    # 步骤4: 按回车
    print("\n[4/4] 按回车发送...")
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
    
    # 默认参数
    x = 1228
    y = 720
    text = "继续"
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        # 如果第一个参数是数字，认为是坐标
        if sys.argv[1].isdigit():
            x = int(sys.argv[1])
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                y = int(sys.argv[2])
                text = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "继续"
            else:
                text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "继续"
        else:
            # 否则认为是文本
            text = " ".join(sys.argv[1:])
    
    print(f"\n📝 将要输入: {text}")
    print(f"📍 目标位置: ({x}, {y})")
    print("\n⏰ 3 秒后开始...")
    print("💡 提示：请确保 Kiro 窗口可见\n")
    
    time.sleep(3)
    
    input_continue_at_position(x, y, text)
