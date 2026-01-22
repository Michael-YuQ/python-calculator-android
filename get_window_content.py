"""
通过句柄获取窗口内容
支持多种方法：
1. Win32 API - 获取窗口文本
2. UI Automation - 获取可访问性树
3. 截图 OCR - 识别屏幕文字
4. 内存读取 - 读取进程内存（高级）
"""

import win32gui
import win32api
import win32con
import win32process
import time
import json


def get_window_text_by_handle(hwnd):
    """方法1: 使用 Win32 API 获取窗口文本"""
    
    print("\n" + "=" * 60)
    print("方法1: Win32 API 获取窗口文本")
    print("=" * 60)
    
    try:
        # 获取窗口标题
        title = win32gui.GetWindowText(hwnd)
        print(f"窗口标题: {title}")
        
        # 获取类名
        class_name = win32gui.GetClassName(hwnd)
        print(f"窗口类名: {class_name}")
        
        # 获取窗口矩形
        rect = win32gui.GetWindowRect(hwnd)
        print(f"窗口位置: {rect}")
        
        # 遍历所有子窗口
        print("\n子窗口内容:")
        
        def enum_child(child_hwnd, results):
            try:
                child_text = win32gui.GetWindowText(child_hwnd)
                child_class = win32gui.GetClassName(child_hwnd)
                
                if child_text or child_class in ['Edit', 'RichEdit', 'RICHEDIT50W']:
                    results.append({
                        'hwnd': child_hwnd,
                        'class': child_class,
                        'text': child_text
                    })
                    
                    if child_text:
                        print(f"  [{child_hwnd}] {child_class}: {child_text[:100]}")
            except:
                pass
            
            return True
        
        results = []
        win32gui.EnumChildWindows(hwnd, enum_child, results)
        
        if not results:
            print("  (未找到包含文本的子窗口)")
        
        return results
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def get_window_content_uiautomation(hwnd):
    """方法2: 使用 UI Automation 获取内容"""
    
    print("\n" + "=" * 60)
    print("方法2: UI Automation 获取内容")
    print("=" * 60)
    
    try:
        from comtypes.client import CreateObject, GetModule
        
        # 加载 UI Automation
        GetModule('UIAutomationCore.dll')
        import comtypes.gen.UIAutomationClient as UIA
        
        automation = CreateObject(
            '{ff48dba4-60ef-4201-aa87-54103eef594e}',
            interface=UIA.IUIAutomation
        )
        
        # 从句柄获取元素
        element = automation.ElementFromHandle(hwnd)
        
        if not element:
            print("❌ 无法获取 UI Automation 元素")
            return []
        
        print(f"✅ 根元素:")
        print(f"   名称: {element.CurrentName}")
        print(f"   类名: {element.CurrentClassName}")
        print(f"   控件类型: {element.CurrentControlType}")
        
        # 查找所有文本元素
        print("\n📋 文本元素:")
        
        # 查找 Text 控件
        text_condition = automation.CreatePropertyCondition(
            UIA.UIA_ControlTypePropertyId,
            UIA.UIA_TextControlTypeId
        )
        
        text_elements = element.FindAll(UIA.TreeScope_Descendants, text_condition)
        
        results = []
        
        for i in range(min(text_elements.Length, 50)):  # 限制数量
            try:
                text_elem = text_elements.GetElement(i)
                name = text_elem.CurrentName
                
                if name and len(name.strip()) > 0:
                    results.append({
                        'type': 'Text',
                        'name': name,
                        'class': text_elem.CurrentClassName
                    })
                    
                    print(f"  [{i}] {name[:100]}")
            except:
                pass
        
        # 查找 Edit 控件
        print("\n📝 输入框内容:")
        
        edit_condition = automation.CreatePropertyCondition(
            UIA.UIA_ControlTypePropertyId,
            UIA.UIA_EditControlTypeId
        )
        
        edit_elements = element.FindAll(UIA.TreeScope_Descendants, edit_condition)
        
        for i in range(min(edit_elements.Length, 20)):
            try:
                edit_elem = edit_elements.GetElement(i)
                name = edit_elem.CurrentName
                
                # 尝试获取值
                try:
                    value_pattern = edit_elem.GetCurrentPattern(UIA.UIA_ValuePatternId)
                    value = value_pattern.CurrentValue
                    
                    if value:
                        results.append({
                            'type': 'Edit',
                            'name': name,
                            'value': value,
                            'class': edit_elem.CurrentClassName
                        })
                        
                        print(f"  [{i}] {name}: {value[:100]}")
                except:
                    if name:
                        print(f"  [{i}] {name}")
            except:
                pass
        
        # 查找 Document 控件（可能包含富文本）
        print("\n📄 文档内容:")
        
        doc_condition = automation.CreatePropertyCondition(
            UIA.UIA_ControlTypePropertyId,
            UIA.UIA_DocumentControlTypeId
        )
        
        doc_elements = element.FindAll(UIA.TreeScope_Descendants, doc_condition)
        
        for i in range(min(doc_elements.Length, 10)):
            try:
                doc_elem = doc_elements.GetElement(i)
                name = doc_elem.CurrentName
                
                # 尝试获取文本模式
                try:
                    text_pattern = doc_elem.GetCurrentPattern(UIA.UIA_TextPatternId)
                    text_range = text_pattern.DocumentRange
                    text = text_range.GetText(-1)  # -1 表示获取所有文本
                    
                    if text:
                        results.append({
                            'type': 'Document',
                            'name': name,
                            'text': text,
                            'class': doc_elem.CurrentClassName
                        })
                        
                        print(f"  [{i}] {name}:")
                        print(f"      {text[:200]}")
                except:
                    if name:
                        print(f"  [{i}] {name}")
            except:
                pass
        
        if not results:
            print("  (未找到内容)")
        
        return results
        
    except ImportError:
        print("❌ 需要安装 comtypes 库")
        print("   运行: pip install comtypes")
        return []
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_window_content_screenshot(hwnd):
    """方法3: 截图并 OCR 识别"""
    
    print("\n" + "=" * 60)
    print("方法3: 截图 OCR 识别")
    print("=" * 60)
    
    try:
        from PIL import ImageGrab
        import pytesseract
        
        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        
        print(f"窗口位置: {rect}")
        print("📸 截图中...")
        
        # 截图
        screenshot = ImageGrab.grab(bbox=rect)
        screenshot.save('window_screenshot.png')
        
        print("✅ 截图已保存: window_screenshot.png")
        print("🔍 OCR 识别中...")
        
        # OCR 识别
        text = pytesseract.image_to_string(screenshot, lang='chi_sim+eng')
        
        print("\n识别结果:")
        print("-" * 60)
        print(text)
        print("-" * 60)
        
        return [{'type': 'OCR', 'text': text}]
        
    except ImportError as e:
        print(f"❌ 需要安装依赖库:")
        print("   pip install pillow pytesseract")
        print("   并安装 Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        return []
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def get_process_memory_strings(hwnd):
    """方法4: 读取进程内存中的字符串（高级）"""
    
    print("\n" + "=" * 60)
    print("方法4: 读取进程内存")
    print("=" * 60)
    
    try:
        import ctypes
        from ctypes import wintypes
        
        # 获取进程 ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        print(f"进程 ID: {pid}")
        
        # 打开进程
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        
        process_handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
            False,
            pid
        )
        
        if not process_handle:
            print("❌ 无法打开进程（可能需要管理员权限）")
            return []
        
        print("✅ 进程已打开")
        print("⚠️  注意：读取进程内存需要管理员权限，且可能不稳定")
        
        # 这里需要更复杂的内存扫描逻辑
        # 简化版本：只显示提示
        print("\n💡 完整的内存读取需要:")
        print("   1. 管理员权限")
        print("   2. 了解目标进程的内存布局")
        print("   3. 使用专门的内存扫描工具")
        
        ctypes.windll.kernel32.CloseHandle(process_handle)
        
        return []
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def get_all_window_content(hwnd):
    """综合使用所有方法获取窗口内容"""
    
    print("=" * 60)
    print("获取窗口内容")
    print("=" * 60)
    
    # 获取窗口信息
    try:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        
        print(f"\n目标窗口:")
        print(f"  句柄: {hwnd}")
        print(f"  标题: {title}")
        print(f"  类名: {class_name}")
    except:
        print(f"❌ 无效的窗口句柄: {hwnd}")
        return
    
    all_results = {}
    
    # 方法1: Win32 API
    results1 = get_window_text_by_handle(hwnd)
    all_results['win32'] = results1
    
    # 方法2: UI Automation
    results2 = get_window_content_uiautomation(hwnd)
    all_results['uiautomation'] = results2
    
    # 方法3: 截图 OCR（可选）
    # results3 = get_window_content_screenshot(hwnd)
    # all_results['ocr'] = results3
    
    # 方法4: 内存读取（高级，可选）
    # results4 = get_process_memory_strings(hwnd)
    # all_results['memory'] = results4
    
    # 保存结果
    print("\n" + "=" * 60)
    print("保存结果")
    print("=" * 60)
    
    output_file = f'window_content_{hwnd}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 结果已保存到: {output_file}")
    
    # 统计
    total = sum(len(v) if isinstance(v, list) else 0 for v in all_results.values())
    print(f"\n📊 共获取 {total} 条内容")
    
    return all_results


def find_kiro_and_get_content():
    """查找 Kiro 窗口并获取内容"""
    
    print("🔍 查找 Kiro 窗口...")
    
    def find_window(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Kiro" in title:
                results.append((hwnd, title))
        return True
    
    results = []
    win32gui.EnumWindows(find_window, results)
    
    if not results:
        print("❌ 未找到 Kiro 窗口")
        return
    
    hwnd, title = results[0]
    print(f"✅ 找到窗口: {title}")
    
    get_all_window_content(hwnd)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 使用指定的句柄
        hwnd = int(sys.argv[1])
        get_all_window_content(hwnd)
    else:
        # 等待3秒后获取当前窗口
        print("⏰ 3 秒后获取当前前台窗口的内容...")
        print("💡 请切换到目标窗口")
        time.sleep(3)
        
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        
        print(f"\n当前窗口: {title}")
        print(f"句柄: {hwnd}")
        
        get_all_window_content(hwnd)
