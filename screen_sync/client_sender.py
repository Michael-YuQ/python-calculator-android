"""
屏幕同步 - 发送端（客户端）
捕获屏幕右侧 1/4 区域，每秒 4 帧发送到服务器
"""

import socket
import time
import struct
import io
from PIL import ImageGrab
import threading
import json


class ScreenSender:
    def __init__(self, server_host='111.170.6.103', server_port=5003, fps=4):
        self.server_host = server_host
        self.server_port = server_port
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.running = False
        self.socket = None
        self.stats = {
            'frames_sent': 0,
            'bytes_sent': 0,
            'errors': 0,
            'start_time': None
        }
    
    def get_screen_region(self):
        """获取屏幕右侧 1/4 区域（左边界向左扩展 20px）"""
        # 获取屏幕尺寸
        screen = ImageGrab.grab()
        width, height = screen.size
        
        # 计算右侧 1/4 区域，左边界向左移动 20px
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
            
            # 压缩为 JPEG
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=75, optimize=True)
            
            return buffer.getvalue()
        
        except Exception as e:
            print(f"❌ 捕获失败: {e}")
            return None
    
    def connect(self):
        """连接到服务器"""
        try:
            print(f"🔌 连接到服务器 {self.server_host}:{self.server_port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            print("✅ 已连接到服务器")
            
            # 发送配置信息
            region = self.get_screen_region()
            config = {
                'fps': self.fps,
                'region': region,
                'width': region[2] - region[0],
                'height': region[3] - region[1]
            }
            
            config_json = json.dumps(config).encode('utf-8')
            self.socket.sendall(struct.pack('!I', len(config_json)))
            self.socket.sendall(config_json)
            
            print(f"📐 区域: {region}")
            print(f"📊 分辨率: {config['width']}x{config['height']}")
            print(f"🎬 帧率: {self.fps} FPS")
            
            return True
        
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def send_frame(self, frame_data):
        """发送一帧数据"""
        try:
            # 发送帧大小
            frame_size = len(frame_data)
            self.socket.sendall(struct.pack('!I', frame_size))
            
            # 发送帧数据
            self.socket.sendall(frame_data)
            
            self.stats['frames_sent'] += 1
            self.stats['bytes_sent'] += frame_size
            
            return True
        
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def print_stats(self):
        """打印统计信息"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            fps = self.stats['frames_sent'] / elapsed if elapsed > 0 else 0
            mbps = (self.stats['bytes_sent'] * 8 / 1024 / 1024) / elapsed if elapsed > 0 else 0
            
            print(f"\r📊 帧数: {self.stats['frames_sent']} | "
                  f"FPS: {fps:.1f} | "
                  f"速率: {mbps:.2f} Mbps | "
                  f"错误: {self.stats['errors']}", end='')
    
    def start(self):
        """开始发送"""
        if not self.connect():
            return
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        print("\n🚀 开始发送屏幕...")
        print("💡 按 Ctrl+C 停止\n")
        
        try:
            while self.running:
                frame_start = time.time()
                
                # 捕获帧
                frame_data = self.capture_frame()
                
                if frame_data:
                    # 发送帧
                    if not self.send_frame(frame_data):
                        print("\n⚠️  发送失败，尝试重连...")
                        if not self.connect():
                            break
                
                # 打印统计
                if self.stats['frames_sent'] % 4 == 0:
                    self.print_stats()
                
                # 控制帧率
                elapsed = time.time() - frame_start
                sleep_time = self.frame_interval - elapsed
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  停止发送")
        
        finally:
            self.stop()
    
    def stop(self):
        """停止发送"""
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
            print(f"发送帧数: {self.stats['frames_sent']}")
            print(f"平均 FPS: {self.stats['frames_sent'] / elapsed:.1f}")
            print(f"总数据量: {self.stats['bytes_sent'] / 1024 / 1024:.2f} MB")
            print(f"平均速率: {(self.stats['bytes_sent'] * 8 / 1024 / 1024) / elapsed:.2f} Mbps")
            print(f"错误次数: {self.stats['errors']}")
        
        print("=" * 60)


if __name__ == "__main__":
    import sys
    
    # 默认参数
    host = '111.170.6.103'
    port = 5003
    fps = 4
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        fps = int(sys.argv[3])
    
    print("=" * 60)
    print("屏幕同步 - 发送端")
    print("=" * 60)
    print(f"服务器: {host}:{port}")
    print(f"帧率: {fps} FPS")
    print("=" * 60)
    
    sender = ScreenSender(host, port, fps)
    sender.start()
