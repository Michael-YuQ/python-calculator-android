"""
Kiro DOM 检查器
通过 Chrome DevTools Protocol 连接到 Kiro 并查询 DOM 结构
"""

import json
import time
import subprocess
import sys


def check_cdp_connection():
    """检查是否可以连接到 Chrome DevTools Protocol"""
    
    try:
        import requests
        
        print("🔍 检查 DevTools 连接...")
        response = requests.get('http://localhost:9222/json', timeout=2)
        
        if response.status_code == 200:
            pages = response.json()
            print(f"✅ 已连接到 DevTools，找到 {len(pages)} 个页面")
            return True, pages
        else:
            print("❌ 无法连接到 DevTools")
            return False, []
    
    except ImportError:
        print("❌ 需要安装 requests 库")
        print("   运行: pip install requests websocket-client")
        return False, []
    
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False, []


def connect_websocket(ws_url):
    """连接到 WebSocket 并执行 JavaScript"""
    
    try:
        import websocket
        
        ws = websocket.create_connection(ws_url)
        return ws
    
    except ImportError:
        print("❌ 需要安装 websocket-client 库")
        print("   运行: pip install websocket-client")
        return None
    
    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")
        return None


def execute_js(ws, js_code):
    """在页面中执行 JavaScript 代码"""
    
    if not ws:
        return None
    
    try:
        # 发送命令
        command = {
            "id": int(time.time() * 1000),
            "method": "Runtime.evaluate",
            "params": {
                "expression": js_code,
                "returnByValue": True
            }
        }
        
        ws.send(json.dumps(command))
        
        # 接收响应
        response = ws.recv()
        result = json.loads(response)
        
        if "result" in result and "result" in result["result"]:
            return result["result"]["result"].get("value")
        
        return result
    
    except Exception as e:
        print(f"⚠️ 执行失败: {e}")
        return None


def find_input_elements(ws):
    """查找所有输入元素"""
    
    print("\n🔍 查找所有输入元素...")
    
    js_code = """
    (function() {
        const inputs = document.querySelectorAll('input, textarea, [contenteditable="true"]');
        const results = [];
        
        inputs.forEach((input, index) => {
            const rect = input.getBoundingClientRect();
            results.push({
                index: index,
                tag: input.tagName,
                type: input.type || 'N/A',
                id: input.id || '',
                className: input.className || '',
                placeholder: input.placeholder || '',
                name: input.name || '',
                value: input.value || input.textContent || '',
                position: {
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                },
                visible: rect.width > 0 && rect.height > 0
            });
        });
        
        return results;
    })();
    """
    
    result = execute_js(ws, js_code)
    
    if result:
        print(f"\n✅ 找到 {len(result)} 个输入元素:\n")
        
        for item in result:
            if item['visible']:
                print(f"[{item['index']}] {item['tag']} ({item['type']})")
                
                if item['id']:
                    print(f"    ID: {item['id']}")
                if item['className']:
                    print(f"    Class: {item['className'][:50]}")
                if item['placeholder']:
                    print(f"    Placeholder: {item['placeholder']}")
                if item['name']:
                    print(f"    Name: {item['name']}")
                
                pos = item['position']
                print(f"    位置: ({pos['x']}, {pos['y']}) 大小: {pos['width']}x{pos['height']}")
                
                if item['value']:
                    print(f"    当前值: {item['value'][:50]}")
                
                print()
        
        return result
    
    return []


def get_element_at_position(ws, x, y):
    """获取指定位置的元素"""
    
    print(f"\n🔍 查找位置 ({x}, {y}) 的元素...")
    
    js_code = f"""
    (function() {{
        const element = document.elementFromPoint({x}, {y});
        
        if (!element) return null;
        
        const rect = element.getBoundingClientRect();
        
        return {{
            tag: element.tagName,
            id: element.id || '',
            className: element.className || '',
            type: element.type || '',
            placeholder: element.placeholder || '',
            name: element.name || '',
            value: element.value || element.textContent || '',
            position: {{
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height)
            }},
            selector: element.id ? '#' + element.id : element.tagName.toLowerCase()
        }};
    }})();
    """
    
    result = execute_js(ws, js_code)
    
    if result:
        print(f"\n✅ 找到元素:")
        print(f"   标签: {result['tag']}")
        
        if result['id']:
            print(f"   ID: {result['id']}")
        if result['className']:
            print(f"   Class: {result['className'][:50]}")
        if result['type']:
            print(f"   Type: {result['type']}")
        if result['placeholder']:
            print(f"   Placeholder: {result['placeholder']}")
        
        pos = result['position']
        print(f"   位置: ({pos['x']}, {pos['y']}) 大小: {pos['width']}x{pos['height']}")
        print(f"   选择器: {result['selector']}")
        
        return result
    
    return None


def input_text_to_element(ws, selector, text):
    """向指定元素输入文本"""
    
    print(f"\n⌨️  向元素 {selector} 输入文本...")
    
    js_code = f"""
    (function() {{
        const element = document.querySelector('{selector}');
        
        if (!element) return {{ success: false, error: '元素未找到' }};
        
        // 聚焦元素
        element.focus();
        
        // 设置值
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {{
            element.value = '{text}';
            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }} else if (element.contentEditable === 'true') {{
            element.textContent = '{text}';
            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        
        return {{ success: true }};
    }})();
    """
    
    result = execute_js(ws, js_code)
    
    if result and result.get('success'):
        print("✅ 文本已输入")
        return True
    else:
        print(f"❌ 输入失败: {result.get('error', '未知错误')}")
        return False


def press_enter_on_element(ws, selector):
    """在指定元素上按回车"""
    
    print(f"\n⏎  在元素 {selector} 上按回车...")
    
    js_code = f"""
    (function() {{
        const element = document.querySelector('{selector}');
        
        if (!element) return {{ success: false, error: '元素未找到' }};
        
        // 触发回车事件
        const event = new KeyboardEvent('keydown', {{
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13,
            bubbles: true
        }});
        
        element.dispatchEvent(event);
        
        return {{ success: true }};
    }})();
    """
    
    result = execute_js(ws, js_code)
    
    if result and result.get('success'):
        print("✅ 已按回车")
        return True
    else:
        print(f"❌ 失败: {result.get('error', '未知错误')}")
        return False


def main():
    """主函数"""
    
    print("=" * 60)
    print("Kiro DOM 检查器")
    print("=" * 60)
    
    # 检查连接
    connected, pages = check_cdp_connection()
    
    if not connected:
        print("\n" + "=" * 60)
        print("💡 如何启用 DevTools Protocol:")
        print("=" * 60)
        print("\n方法1: 在 Kiro 中按 Ctrl+Shift+I 打开开发者工具")
        print("       然后在 Console 中手动执行 JavaScript")
        print("\n方法2: 使用启动参数（如果支持）:")
        print("       kiro.exe --remote-debugging-port=9222")
        print("\n方法3: 使用现有的位置点击方案:")
        print("       python kiro_auto_input.py")
        print("=" * 60)
        return
    
    # 选择页面
    if not pages:
        print("❌ 没有找到可用的页面")
        return
    
    print(f"\n找到 {len(pages)} 个页面:")
    for i, page in enumerate(pages):
        print(f"  [{i}] {page.get('title', 'Untitled')}")
    
    # 使用第一个页面
    page = pages[0]
    ws_url = page.get('webSocketDebuggerUrl')
    
    if not ws_url:
        print("❌ 无法获取 WebSocket URL")
        return
    
    print(f"\n连接到: {page.get('title', 'Untitled')}")
    
    # 连接 WebSocket
    ws = connect_websocket(ws_url)
    
    if not ws:
        return
    
    print("✅ WebSocket 已连接")
    
    try:
        # 查找所有输入元素
        inputs = find_input_elements(ws)
        
        # 查找特定位置的元素
        if len(sys.argv) > 1:
            x = int(sys.argv[1])
            y = int(sys.argv[2]) if len(sys.argv) > 2 else 720
            
            element = get_element_at_position(ws, x, y)
            
            # 如果提供了文本，则输入
            if len(sys.argv) > 3 and element:
                text = " ".join(sys.argv[3:])
                selector = f"#{element['id']}" if element['id'] else element['selector']
                
                input_text_to_element(ws, selector, text)
                press_enter_on_element(ws, selector)
        
        # 保存结果
        if inputs:
            with open('kiro_inputs.json', 'w', encoding='utf-8') as f:
                json.dump(inputs, f, indent=2, ensure_ascii=False)
            
            print("\n💾 输入元素信息已保存到: kiro_inputs.json")
    
    finally:
        ws.close()
        print("\n✅ 连接已关闭")


if __name__ == "__main__":
    main()
