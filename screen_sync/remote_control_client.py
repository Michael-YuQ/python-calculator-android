"""
远程控制客户端
- 5003 端口：屏幕共享控制（接收开启/关闭命令）
- 5004 端口：命令接收（接收文本命令并在 Kiro 中执行）
"""

import socket
import threading
import time
import json
import struct
import io
from PIL import ImageGrab
import win32gui
import win32api
import win32con


class RemoteControlClient:
    def __init__(self, server_host='111.170.6.103', 
                 screen_port=5003, command_port=5004):
        self.server_host = server_host
        self.screen_port = screen_port
        self.command_port = command_port
        
        # 屏幕共享状态
        self.screen_sharing_enabled = False
        self.screen_socket = None
        self.screen_thread = None
        
        # 命令接收
        self.command_socket = None
        self.command_thread = None
        
        # 运行状态
        self.running = False
        
        # Kiro 输入位置
        self.kiro_input_position = (1228, 720)
    
    def start(self):
        """启动远程控制客户端"""
        self.running = True
        
        print("=" * 60)
        print("远程控制客户端")
        print("=" * 60)
        print(f"服务器: {self.server_host}")
        print(f"屏幕共享端口: {self.screen_port}")
        print(f"命令接收端口: {self.command_port}")
        print("=" * 60)
        
        # 启动屏幕共享控制线程
        self.screen_thread = threading.Thread(
            target=self.screen_control_loop,
            daemon=True
        )
        self.screen_thread.start()
        
        # 启动命令接收线程
        self.command_thread = threading.Thread(
            target=self.command_receive_loop,
            daemon=True
        )
        self.command_thread.start()
        
        print("\n✅ 远程控制客户端已启动")
        print("💡 按 Ctrl+C 停止\n")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️  停止远程控制")
            self.stop()
    
    def stop(self):
        """停止客户端"""
        self.running = False
        self.screen_sharing_enabled = False
        
        if self.screen_socket:
            try:
                self.screen_socket.close()
            except:
                pass
        
        if self.command_socket:
            try:
                self.command_socket.close()
            except:
                pass
        
        print("✅ 已停止")
    
    # ==================== 屏幕共享控制 ====================
    
    def screen_control_loop(self):
        """屏幕共享控制循环"""
        while self.running:
            try:
                print(f"\n[屏幕共享] 连接到 {self.server_host}:{self.screen_port}...")
                
                self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.screen_socket.connect((self.server_host, self.screen_port))
                
                print("[屏幕共享] ✅ 已连接")
                
                # 发送配置信息
                region = self.get_screen_region()
                config = {
                    'fps': 4,
                    'region': region,
                    'width': region[2] - region[0],
                    'height': region[3] - region[1],
                    'type': 'controlled_sender'  # 标识为受控发送端
                }
                
                config_json = json.dumps(config).encode('utf-8')
                self.screen_socket.sendall(struct.pack('!I', len(config_json)))
                self.screen_socket.sendall(config_json)
                
                print(f"[屏幕共享] 📐 区域: {region}")
                print(f"[屏幕共享] 📊 分辨率: {config['width']}x{config['height']}")
                print(f"[屏幕共享] ⏸️  等待开启命令...")
                
                # 等待控制命令并发送屏幕
                self.screen_sharing_loop()
            
            except Exception as e:
                print(f"[屏幕共享] ❌ 错误: {e}")
                time.sleep(5)
    
    def screen_sharing_loop(self):
        """屏幕共享循环"""
        frame_interval = 1.0 / 4  # 4 FPS
        
        while self.running:
            try:
                if self.screen_sharing_enabled:
                    # 捕获并发送帧
                    frame_start = time.time()
                    
                    frame_data = self.capture_frame()
                    if frame_data:
                        self.send_frame(frame_data)
                    
                    # 控制帧率
                    elapsed = time.time() - frame_start
                    sleep_time = frame_interval - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                else:
                    # 未开启时，等待
                    time.sleep(0.5)
            
            except Exception as e:
                print(f"[屏幕共享] ❌ 发送错误: {e}")
                break
    
    def get_screen_region(self):
        """获取屏幕右侧 1/4 区域"""
        screen = ImageGrab.grab()
        width, height = screen.size
        
        left = width * 3 // 4 - 20
        top = 0
        right = width
        bottom = height
        
        return (left, top, right, bottom)
    
    def capture_frame(self):
        """捕获一帧"""
        try:
            region = self.get_screen_region()
            screenshot = ImageGrab.grab(bbox=region)
            
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=75, optimize=True)
            
            return buffer.getvalue()
        except Exception as e:
            print(f"[屏幕共享] ❌ 捕获失败: {e}")
            return None
    
    def send_frame(self, frame_data):
        """发送一帧"""
        try:
            frame_size = len(frame_data)
            self.screen_socket.sendall(struct.pack('!I', frame_size))
            self.screen_socket.sendall(frame_data)
            return True
        except Exception as e:
            print(f"[屏幕共享] ❌ 发送失败: {e}")
            return False
    
    # ==================== 命令接收 ====================
    
    def command_receive_loop(self):
        """命令接收循环"""
        while self.running:
            try:
                print(f"\n[命令接收] 连接到 {self.server_host}:{self.command_port}...")
                
                self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.command_socket.connect((self.server_host, self.command_port))
                
                print("[命令接收] ✅ 已连接")
                print("[命令接收] 📡 等待命令...\n")
                
                # 接收命令
                while self.running:
                    # 接收命令长度
                    size_data = self.recv_exact(self.command_socket, 4)
                    if not size_data:
                        break
                    
                    cmd_size = struct.unpack('!I', size_data)[0]
                    
                    # 接收命令数据
                    cmd_data = self.recv_exact(self.command_socket, cmd_size)
                    if not cmd_data:
                        break
                    
                    # 解析命令
                    command = json.loads(cmd_data.decode('utf-8'))
                    self.handle_command(command)
            
            except Exception as e:
                print(f"[命令接收] ❌ 错误: {e}")
                time.sleep(5)
    
    def recv_exact(self, sock, size):
        """接收指定大小的数据"""
        data = b''
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def handle_command(self, command):
        """处理命令"""
        cmd_type = command.get('type')
        
        print(f"\n[命令] 收到: {command}")
        
        if cmd_type == 'screen_control':
            # 屏幕共享控制
            action = command.get('action')
            
            if action == 'start':
                self.screen_sharing_enabled = True
                print("[命令] ✅ 屏幕共享已开启")
            
            elif action == 'stop':
                self.screen_sharing_enabled = False
                print("[命令] ⏸️  屏幕共享已停止")
        
        elif cmd_type == 'kiro_input':
            # Kiro 输入命令
            text = command.get('text', '')
            
            if text:
                print(f"[命令] ⌨️  执行 Kiro 输入: {text}")
                self.input_to_kiro(text)
            else:
                print("[命令] ⚠️  命令文本为空")
        
        else:
            print(f"[命令] ⚠️  未知命令类型: {cmd_type}")
    
    # ==================== Kiro 输入 ====================
    
    def input_to_kiro(self, text):
        """在 Kiro 中输入文本"""
        try:
            # 1. 查找并激活 Kiro 窗口
            hwnd = self.find_kiro_window()
            
            if not hwnd:
                print("[Kiro] ❌ 未找到 Kiro 窗口")
                return False
            
            # 激活窗口
            self.activate_window(hwnd)
            time.sleep(0.5)
            
            # 2. 移动鼠标到输入位置
            x, y = self.kiro_input_position
            win32api.SetCursorPos((x, y))
            time.sleep(0.3)
            
            # 3. 点击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.3)
            
            # 4. 输入文本（使用剪贴板）
            self.paste_text(text)
            time.sleep(0.3)
            
            # 5. 按回车
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            print(f"[Kiro] ✅ 已输入: {text}")
            return True
        
        except Exception as e:
            print(f"[Kiro] ❌ 输入失败: {e}")
            return False
    
    def find_kiro_window(self):
        """查找 Kiro 窗口"""
        def find_window(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Kiro" in title:
                    results.append(hwnd)
            return True
        
        results = []
        win32gui.EnumWindows(find_window, results)
        
        return results[0] if results else None
    
    def activate_window(self, hwnd):
        """激活窗口"""
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
            
            win32gui.SetForegroundWindow(hwnd)
        except:
            # 如果失败，尝试 Alt+Tab
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def paste_text(self, text):
        """使用剪贴板粘贴文本"""
        try:
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
        
        except Exception as e:
            print(f"[Kiro] ⚠️  剪贴板粘贴失败: {e}")


if __name__ == "__main__":
    import sys
    
    # 默认参数
    server_host = '111.170.6.103'
    screen_port = 5003
    command_port = 5004
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    if len(sys.argv) > 2:
        screen_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        command_port = int(sys.argv[3])
    
    client = RemoteControlClient(server_host, screen_port, command_port)
    client.start()
