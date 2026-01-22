"""
获取当前焦点控件的句柄
等待3秒后，获取你光标所在的可输入控件的句柄
"""

import win32gui
import win32api
import time
import ctypes


def get_focused_control():
    """获取当前拥有焦点的控件句柄"""
    
    print("⏰ 3 秒倒计时，请将光标放在目标输入框...")
    for i in range(3, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print("\n")
    
    print("🔍 正在获取焦点控件...")
    
    # 方法1：获取前台窗口
    foreground_hwnd = win32gui.GetForegroundWindow()
    foreground_title = win32gui.GetWindowText(foreground_hwnd)
    print(f"\n✅ 前台窗口: {foreground_title}")
    print(f"   句柄: {foreground_hwnd}")
    
    # 方法2：获取焦点控件（使用 GetFocus）
    # 注意：GetFocus 只能获取当前线程的焦点
    try:
        # 获取前台窗口的线程ID
        foreground_thread = win32api.GetWindowThreadProcessId(foreground_hwnd)[0]
        current_thread = win32api.GetCurrentThreadId()
        
        # 附加到前台窗口的线程
        if foreground_thread != current_thread:
            ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, True)
        
        # 获取焦点控件
        focus_hwnd = win32gui.GetFocus()
        
        if focus_hwnd:
            focus_class = win32gui.GetClassName(focus_hwnd)
            focus_text = win32gui.GetWindowText(focus_hwnd)
            
            print(f"\n✅ 焦点控件:")
            print(f"   句柄: {focus_hwnd}")
            print(f"   类名: {focus_class}")
            print(f"   文本: {focus_text}")
            
            # 分离线程
            if foreground_thread != current_thread:
                ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, False)
            
            return focus_hwnd, focus_class
        else:
            print("⚠️ 无法获取焦点控件")
            
            # 分离线程
            if foreground_thread != current_thread:
                ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, False)
    
    except Exception as e:
        print(f"⚠️ GetFocus 失败: {e}")
    
    # 方法3：获取光标位置下的控件
    print("\n🔍 尝试通过光标位置获取控件...")
    
    try:
        # 获取光标位置
        cursor_pos = win32gui.GetCursorPos()
        print(f"   光标位置: {cursor_pos}")
        
        # 获取光标位置的窗口
        point_hwnd = win32gui.WindowFromPoint(cursor_pos)
        
        if point_hwnd:
            point_class = win32gui.GetClassName(point_hwnd)
            point_text = win32gui.GetWindowText(point_hwnd)
            
            print(f"\n✅ 光标位置的控件:")
            print(f"   句柄: {point_hwnd}")
            print(f"   类名: {point_class}")
            print(f"   文本: {point_text}")
            
            return point_hwnd, point_class
    
    except Exception as e:
        print(f"⚠️ WindowFromPoint 失败: {e}")
    
    # 方法4：枚举前台窗口的所有子控件，找到可输入的
    print("\n🔍 枚举前台窗口的所有输入控件...")
    
    def find_editable_controls(hwnd, results):
        try:
            class_name = win32gui.GetClassName(hwnd)
            
            # 常见的可输入控件类名
            editable_classes = ['Edit', 'RichEdit', 'RICHEDIT', 'Chrome', 'Text']
            
            if any(cls in class_name for cls in editable_classes):
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    results.append((hwnd, class_name, text))
        except:
            pass
        return True
    
    editable_controls = []
    win32gui.EnumChildWindows(foreground_hwnd, find_editable_controls, editable_controls)
    
    if editable_controls:
        print(f"\n✅ 找到 {len(editable_controls)} 个可输入控件:")
        for i, (hwnd, class_name, text) in enumerate(editable_controls):
            print(f"   [{i}] 句柄: {hwnd:10d} 类名: {class_name:30s} 文本: {text[:50]}")
        
        # 返回第一个
        return editable_controls[0][0], editable_controls[0][1]
    
    return None, None


def test_input_to_handle(hwnd, text="测试输入"):
    """测试向句柄输入文本"""
    
    if not hwnd:
        print("\n❌ 没有有效的句柄")
        return False
    
    print(f"\n🧪 测试输入到句柄 {hwnd}...")
    print(f"   文本: {text}")
    
    try:
        # 获取父窗口
        parent_hwnd = win32gui.GetParent(hwnd)
        if parent_hwnd:
            # 激活父窗口
            win32gui.SetForegroundWindow(parent_hwnd)
            time.sleep(0.2)
        
        # 方法1：WM_SETTEXT
        win32api.SendMessage(hwnd, 0x000C, 0, text)  # WM_SETTEXT = 0x000C
        time.sleep(0.2)
        
        # 验证
        length = win32gui.SendMessage(hwnd, 0x000E, 0, 0)  # WM_GETTEXTLENGTH = 0x000E
        
        if length > 0:
            print(f"✅ 成功！文本长度: {length}")
            
            # 发送回车
            print("   发送回车...")
            win32api.SendMessage(hwnd, 0x0100, 0x0D, 0)  # WM_KEYDOWN, VK_RETURN
            time.sleep(0.05)
            win32api.SendMessage(hwnd, 0x0101, 0x0D, 0)  # WM_KEYUP, VK_RETURN
            print("✅ 已按回车")
            
            return True
        else:
            print("⚠️ 输入可能失败")
            return False
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("获取焦点控件句柄")
    print("=" * 60)
    print("\n💡 使用方法:")
    print("   1. 运行此脚本")
    print("   2. 在3秒内点击目标输入框")
    print("   3. 脚本会显示该输入框的句柄")
    print()
    
    # 获取焦点控件
    hwnd, class_name = get_focused_control()
    
    if hwnd:
        print("\n" + "=" * 60)
        print("📋 结果:")
        print("=" * 60)
        print(f"句柄: {hwnd}")
        print(f"类名: {class_name}")
        print("\n💡 使用此句柄输入文本:")
        print(f"   python input_by_handle.py {hwnd} 你的文本")
        print("=" * 60)
        
        # 询问是否测试
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            test_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "测试"
            print(f"\n🧪 测试模式: 将输入 '{test_text}'")
            time.sleep(1)
            test_input_to_handle(hwnd, test_text)
    else:
        print("\n❌ 未能获取焦点控件")
        print("💡 提示:")
        print("   - 确保在3秒内点击了输入框")
        print("   - 确保输入框是可见和可用的")
        print("   - 尝试重新运行脚本")
