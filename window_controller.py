"""
Windows 窗口控制器 - 使用 pywin32
功能：获取窗口句柄、查找文本框、输入文本、按回车
"""

import win32gui
import win32con
import win32api
import time


class WindowController:
    """Windows 窗口控制器"""
    
    def __init__(self):
        self.hwnd = None
        self.edit_hwnd = None
    
    def get_current_window(self):
        """获取当前活动窗口"""
        self.hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(self.hwnd)
        print(f"✅ 当前窗口: {title}")
        print(f"   句柄: {self.hwnd}")
        return self.hwnd
    
    def find_window_by_title(self, title):
        """根据标题查找窗口"""
        self.hwnd = win32gui.FindWindow(None, title)
        if self.hwnd:
            print(f"✅ 找到窗口: {title}")
            print(f"   句柄: {self.hwnd}")
        else:
            print(f"❌ 未找到窗口: {title}")
        return self.hwnd
    
    def find_window_by_partial_title(self, partial_title):
        """根据部分标题查找窗口"""
        def callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if partial_title.lower() in title.lower():
                    results.append((hwnd, title))
            return True
        
        results = []
        win32gui.EnumWindows(callback, results)
        
        if results:
            print(f"✅ 找到 {len(results)} 个匹配的窗口:")
            for i, (hwnd, title) in enumerate(results):
                print(f"   [{i}] {title} (句柄: {hwnd})")
            
            # 使用第一个匹配的窗口
            self.hwnd = results[0][0]
            return self.hwnd
        else:
            print(f"❌ 未找到包含 '{partial_title}' 的窗口")
            return None
    
    def list_all_windows(self):
        """列出所有可见窗口"""
        def callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # 只显示有标题的窗口
                    results.append((hwnd, title))
            return True
        
        results = []
        win32gui.EnumWindows(callback, results)
        
        print(f"\n📋 所有可见窗口 (共 {len(results)} 个):")
        for i, (hwnd, title) in enumerate(results):
            print(f"   [{i}] {title}")
        
        return results
    
    def list_child_controls(self):
        """列出窗口的所有子控件"""
        if not self.hwnd:
            print("❌ 请先选择一个窗口")
            return []
        
        def callback(child_hwnd, results):
            class_name = win32gui.GetClassName(child_hwnd)
            text = win32gui.GetWindowText(child_hwnd)
            results.append((child_hwnd, class_name, text))
            return True
        
        results = []
        win32gui.EnumChildWindows(self.hwnd, callback, results)
        
        print(f"\n📋 窗口的子控件 (共 {len(results)} 个):")
        for i, (hwnd, class_name, text) in enumerate(results):
            print(f"   [{i}] 类名: {class_name:20s} 句柄: {hwnd:10d} 文本: {text}")
        
        return results
    
    def find_edit_control(self, index=0):
        """查找文本框控件（Edit 类）"""
        if not self.hwnd:
            print("❌ 请先选择一个窗口")
            return None
        
        def callback(hwnd, results):
            if win32gui.GetClassName(hwnd) == "Edit":
                results.append(hwnd)
            return True
        
        results = []
        win32gui.EnumChildWindows(self.hwnd, callback, results)
        
        if results:
            print(f"✅ 找到 {len(results)} 个文本框")
            if index < len(results):
                self.edit_hwnd = results[index]
                print(f"   使用第 {index} 个文本框 (句柄: {self.edit_hwnd})")
                return self.edit_hwnd
            else:
                print(f"❌ 索引 {index} 超出范围 (0-{len(results)-1})")
                return None
        else:
            print("❌ 未找到文本框控件")
            return None
    
    def get_text(self):
        """获取文本框当前内容"""
        if not self.edit_hwnd:
            print("❌ 请先查找文本框")
            return None
        
        length = win32gui.SendMessage(self.edit_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
        buffer = win32gui.PyMakeBuffer(length + 1)
        win32gui.SendMessage(self.edit_hwnd, win32con.WM_GETTEXT, length + 1, buffer)
        text = buffer[:length].decode('utf-8', errors='ignore')
        print(f"📄 当前文本: {text}")
        return text
    
    def clear_text(self):
        """清空文本框"""
        if not self.edit_hwnd:
            print("❌ 请先查找文本框")
            return False
        
        win32api.SendMessage(self.edit_hwnd, win32con.WM_SETTEXT, 0, "")
        print("🗑️  已清空文本")
        return True
    
    def input_text(self, text):
        """输入文本"""
        if not self.edit_hwnd:
            print("❌ 请先查找文本框")
            return False
        
        # 激活窗口
        win32gui.SetForegroundWindow(self.hwnd)
        time.sleep(0.1)
        
        # 输入文本
        win32api.SendMessage(self.edit_hwnd, win32con.WM_SETTEXT, 0, text)
        print(f"✍️  已输入: {text}")
        return True
    
    def append_text(self, text):
        """追加文本"""
        if not self.edit_hwnd:
            print("❌ 请先查找文本框")
            return False
        
        current = self.get_text()
        new_text = (current or "") + text
        return self.input_text(new_text)
    
    def press_enter(self):
        """按回车键"""
        if not self.edit_hwnd:
            print("❌ 请先查找文本框")
            return False
        
        # 发送回车键按下和释放
        win32api.SendMessage(self.edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        time.sleep(0.05)
        win32api.SendMessage(self.edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
        print("⏎  已按回车")
        return True
    
    def click_button(self, button_text):
        """点击按钮"""
        if not self.hwnd:
            print("❌ 请先选择一个窗口")
            return False
        
        def callback(hwnd, results):
            if win32gui.GetClassName(hwnd) == "Button":
                text = win32gui.GetWindowText(hwnd)
                if button_text.lower() in text.lower():
                    results.append(hwnd)
            return True
        
        results = []
        win32gui.EnumChildWindows(self.hwnd, callback, results)
        
        if results:
            button_hwnd = results[0]
            win32api.SendMessage(button_hwnd, win32con.BM_CLICK, 0, 0)
            print(f"🖱️  已点击按钮: {button_text}")
            return True
        else:
            print(f"❌ 未找到按钮: {button_text}")
            return False


def demo():
    """演示程序"""
    print("=" * 60)
    print("Windows 窗口控制器演示")
    print("=" * 60)
    
    controller = WindowController()
    
    # 1. 列出所有窗口
    print("\n【步骤 1】列出所有窗口")
    controller.list_all_windows()
    
    # 2. 获取当前窗口
    print("\n【步骤 2】获取当前活动窗口")
    print("提示：请在 5 秒内切换到目标窗口...")
    for i in range(5, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print()
    
    controller.get_current_window()
    
    # 3. 列出子控件
    print("\n【步骤 3】列出窗口的所有子控件")
    controller.list_child_controls()
    
    # 4. 查找文本框
    print("\n【步骤 4】查找文本框")
    if controller.find_edit_control(index=0):
        
        # 5. 获取当前文本
        print("\n【步骤 5】获取当前文本")
        controller.get_text()
        
        # 6. 输入文本
        print("\n【步骤 6】输入文本")
        controller.input_text("Hello from Python!")
        time.sleep(1)
        
        # 7. 按回车
        print("\n【步骤 7】按回车键")
        controller.press_enter()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


def interactive_mode():
    """交互模式"""
    controller = WindowController()
    
    print("\n" + "=" * 60)
    print("交互模式 - 输入命令控制窗口")
    print("=" * 60)
    print("\n可用命令:")
    print("  1. list       - 列出所有窗口")
    print("  2. current    - 获取当前窗口")
    print("  3. find       - 查找窗口（输入标题）")
    print("  4. controls   - 列出子控件")
    print("  5. edit       - 查找文本框")
    print("  6. get        - 获取文本")
    print("  7. input      - 输入文本")
    print("  8. enter      - 按回车")
    print("  9. clear      - 清空文本")
    print("  0. quit       - 退出")
    print()
    
    while True:
        cmd = input("请输入命令 > ").strip().lower()
        
        if cmd == "list" or cmd == "1":
            controller.list_all_windows()
        
        elif cmd == "current" or cmd == "2":
            print("请在 3 秒内切换到目标窗口...")
            time.sleep(3)
            controller.get_current_window()
        
        elif cmd == "find" or cmd == "3":
            title = input("输入窗口标题（部分匹配）: ")
            controller.find_window_by_partial_title(title)
        
        elif cmd == "controls" or cmd == "4":
            controller.list_child_controls()
        
        elif cmd == "edit" or cmd == "5":
            index = input("输入文本框索引（默认0）: ").strip()
            index = int(index) if index else 0
            controller.find_edit_control(index)
        
        elif cmd == "get" or cmd == "6":
            controller.get_text()
        
        elif cmd == "input" or cmd == "7":
            text = input("输入文本: ")
            controller.input_text(text)
        
        elif cmd == "enter" or cmd == "8":
            controller.press_enter()
        
        elif cmd == "clear" or cmd == "9":
            controller.clear_text()
        
        elif cmd == "quit" or cmd == "0":
            print("再见！")
            break
        
        else:
            print("❌ 未知命令")
        
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        interactive_mode()
