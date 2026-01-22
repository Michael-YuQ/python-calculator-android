"""
屏幕同步 - 接收端（客户端）
从服务器接收屏幕数据并显示
"""

import socket
import struct
import json
import time
import io
from PIL import Image
import threading
import tkinter as tk
from tkinter import ttk


class ScreenReceiver:
    def __init__(self, server_host='111.170.6.103', server_port=5003, sender_id='default'):
        self.server_host = server_host
        self.server_port = server_port
        self.sender_id = sender_id
        self.running = False
        self.socket = None
        
        self.stats = {
            'frames_received': 0,
            'bytes_received': 0,
            'errors': 0,
            'start_time': None
        }
        
        # GUI
        self.window = None
        self.canvas = None
        self.photo = None
        self.status_label = None
    
    def connect(self):
        """连接到服务器"""
        try:
            print(f"🔌 连接到服务器 {self.server_host}:{self.server_port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            print("✅ 已连接到服务器")
            
            # 发送配置信息（标识为接收端）
            config = {
                'sender_id': self.sender_id
            }
            
            config_json = json.dumps(config).encode('utf-8')
            self.socket.sendall(struct.pack('!I', len(config_json)))
            self.socket.sendall(config_json)
            
            print(f"📡 订阅发送端: {self.sender_id}")
            
            return True
        
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def recv_exact(self, size):
        """接收指定大小的数据"""
        data = b''
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def receive_frame(self):
        """接收一帧"""
        try:
            # 接收帧大小
            size_data = self.recv_exact(4)
            if not size_data:
                return None
            
            frame_size = struct.unpack('!I', size_data)[0]
            
            # 接收帧数据
            frame_data = self.recv_exact(frame_size)
            if not frame_data:
                return None
            
            self.stats['frames_received'] += 1
            self.stats['bytes_received'] += frame_size
            
            # 解码图像
            image = Image.open(io.BytesIO(frame_data))
            
            return image
        
        except Exception as e:
            print(f"❌ 接收失败: {e}")
            self.stats['errors'] += 1
            return None
    
    def create_gui(self):
        """创建 GUI 窗口"""
        self.window = tk.Tk()
        self.window.title(f"屏幕同步 - 接收端 ({self.sender_id})")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 画布
        self.canvas = tk.Canvas(self.window, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="等待连接...")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 设置初始大小
        self.window.geometry("800x600")
    
    def update_frame(self, image):
        """更新显示的帧"""
        if not self.window or not self.canvas:
            return
        
        try:
            # 获取画布大小
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # 缩放图像以适应画布
            img_width, img_height = image.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为 PhotoImage
            from PIL import ImageTk
            self.photo = ImageTk.PhotoImage(resized_image)
            
            # 清除画布
            self.canvas.delete("all")
            
            # 居中显示
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        
        except Exception as e:
            print(f"❌ 更新显示失败: {e}")
    
    def update_status(self):
        """更新状态栏"""
        if not self.status_label:
            return
        
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            fps = self.stats['frames_received'] / elapsed if elapsed > 0 else 0
            mbps = (self.stats['bytes_received'] * 8 / 1024 / 1024) / elapsed if elapsed > 0 else 0
            
            status = (f"帧数: {self.stats['frames_received']} | "
                     f"FPS: {fps:.1f} | "
                     f"速率: {mbps:.2f} Mbps | "
                     f"错误: {self.stats['errors']}")
            
            self.status_label.config(text=status)
    
    def receive_loop(self):
        """接收循环"""
        if not self.connect():
            return
        
        self.stats['start_time'] = time.time()
        
        print("\n🚀 开始接收屏幕...")
        print("💡 关闭窗口停止\n")
        
        frame_count = 0
        
        while self.running:
            # 接收帧
            image = self.receive_frame()
            
            if image:
                # 更新显示
                self.update_frame(image)
                
                # 更新状态
                frame_count += 1
                if frame_count % 4 == 0:
                    self.update_status()
            else:
                print("\n⚠️  接收中断，尝试重连...")
                time.sleep(2)
                
                if not self.connect():
                    break
    
    def start(self):
        """启动接收"""
        self.running = True
        
        # 创建 GUI
        self.create_gui()
        
        # 启动接收线程
        receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        receive_thread.start()
        
        # 运行 GUI
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            pass
        
        self.stop()
    
    def on_closing(self):
        """窗口关闭事件"""
        self.stop()
        if self.window:
            self.window.destroy()
    
    def stop(self):
        """停止接收"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("\n" + "=" * 60)
        print("📊 最终统计")
        print("=" * 60)
        
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            print(f"运行时间: {elapsed:.1f} 秒")
            print(f"接收帧数: {self.stats['frames_received']}")
            print(f"平均 FPS: {self.stats['frames_received'] / elapsed:.1f}")
            print(f"总数据量: {self.stats['bytes_received'] / 1024 / 1024:.2f} MB")
            print(f"平均速率: {(self.stats['bytes_received'] * 8 / 1024 / 1024) / elapsed:.2f} Mbps")
            print(f"错误次数: {self.stats['errors']}")
        
        print("=" * 60)


if __name__ == "__main__":
    import sys
    
    # 默认参数
    host = '111.170.6.103'
    port = 5003
    sender_id = 'default'
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        sender_id = sys.argv[3]
    
    print("=" * 60)
    print("屏幕同步 - 接收端")
    print("=" * 60)
    print(f"服务器: {host}:{port}")
    print(f"发送端 ID: {sender_id}")
    print("=" * 60)
    
    receiver = ScreenReceiver(host, port, sender_id)
    receiver.start()
