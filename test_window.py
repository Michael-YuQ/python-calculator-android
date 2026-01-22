"""
简单测试示例 - 自动化控制记事本
"""

import win32gui
import win32con
import win32api
import time
import subprocess


def test_notepad():
    """测试：自动化控制记事本"""
    print("🚀 启动记事本测试...")
    
    # 1. 打开记事本
    print("\n[1] 启动记事本...")
    subprocess.Popen(['notepad.exe'])
    time.sleep(1)
    
    # 2. 查找记事本窗口
    print("[2] 查找记事本窗口...")
    hwnd = win32gui.FindWindow(None, "无标题 - 记事本")
    if not hwnd:
        hwnd = win32gui.FindWindow(None, "Untitled - Notepad")
    
    if not hwnd:
        print("❌ 未找到记事本窗口")
        return
    
    print(f"✅ 找到记事本 (句柄: {hwnd})")
    
    # 3. 查找文本框
    print("[3] 查找文本框...")
    def find_edit(hwnd, results):
        if win32gui.GetClassName(hwnd) == "Edit":
            results.append(hwnd)
        return True
    
    results = []
    win32gui.EnumChildWindows(hwnd, find_edit, results)
    
    if not results:
        print("❌ 未找到文本框")
        return
    
    edit_hwnd = results[0]
    print(f"✅ 找到文本框 (句柄: {edit_hwnd})")
    
    # 4. 激活窗口
    print("[4] 激活窗口...")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    # 5. 输入文本
    print("[5] 输入文本...")
    text = "Hello from Python!\n这是自动输入的文本。\n测试成功！"
    win32api.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, text)
    print(f"✅ 已输入文本")
    
    # 6. 等待查看
    print("\n✨ 测试完成！记事本中应该显示了文本。")
    print("   窗口将保持打开，你可以手动关闭。")


def test_current_window():
    """测试：控制当前窗口"""
    print("🚀 当前窗口测试...")
    print("⏰ 请在 5 秒内切换到目标窗口（包含文本框）...")
    
    for i in range(5, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print()
    
    # 获取当前窗口
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    print(f"✅ 当前窗口: {title} (句柄: {hwnd})")
    
    # 查找文本框
    def find_edit(child_hwnd, results):
        if win32gui.GetClassName(child_hwnd) == "Edit":
            results.append(child_hwnd)
        return True
    
    results = []
    win32gui.EnumChildWindows(hwnd, find_edit, results)
    
    if not results:
        print("❌ 未找到文本框")
        return
    
    edit_hwnd = results[0]
    print(f"✅ 找到 {len(results)} 个文本框，使用第一个")
    
    # 输入文本
    text = "自动输入测试 - " + time.strftime("%H:%M:%S")
    win32api.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, text)
    print(f"✅ 已输入: {text}")
    
    # 按回车
    time.sleep(0.5)
    win32api.SendMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.05)
    win32api.SendMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    print("✅ 已按回车")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Windows 窗口控制测试")
    print("=" * 60)
    print("\n选择测试:")
    print("  1. 自动化控制记事本（推荐）")
    print("  2. 控制当前窗口")
    print()
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        test_notepad()
    elif choice == "2":
        test_current_window()
    else:
        print("❌ 无效选择")
