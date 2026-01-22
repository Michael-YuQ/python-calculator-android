"""
屏幕同步 - 服务器端
接收客户端发送的屏幕数据，转发给接收端
支持多个客户端和多个接收端
"""

import socket
import threading
import struct
import json
import time
from collections import defaultdict


class ScreenServer:
    def __init__(self, host='0.0.0.0', port=5003):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        
        # 客户端连接（发送端）
        self.senders = {}  # {client_id: {'socket': socket, 'config': config, 'stats': stats}}
        self.sender_lock = threading.Lock()
        
        # 接收端连接
        self.receivers = {}  # {client_id: [socket1, socket2, ...]}
        self.receiver_lock = threading.Lock()
        
        # 统计
        self.stats = {
            'total_frames': 0,
            'total_bytes': 0,
            'start_time': None
        }
    
    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            self.running = True
            self.stats['start_time'] = time.time()
            
            print("=" * 60)
            print("屏幕同步服务器")
            print("=" * 60)
            print(f"✅ 服务器启动: {self.host}:{self.port}")
            print("💡 等待连接...\n")
            
            # 启动统计线程
            stats_thread = threading.Thread(target=self.print_stats_loop, daemon=True)
            stats_thread.start()
            
            # 接受连接
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"\n🔌 新连接: {client_address}")
                    
                    # 启动处理线程
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    thread.start()
                
                except Exception as e:
                    if self.running:
                        print(f"❌ 接受连接失败: {e}")
        
        except Exception as e:
            print(f"❌ 服务器启动失败: {e}")
        
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """处理客户端连接"""
        try:
            # 接收客户端类型（sender 或 receiver）
            client_socket.settimeout(5.0)
            
            # 接收配置信息长度
            size_data = self.recv_exact(client_socket, 4)
            if not size_data:
                print(f"⚠️  {client_address} 未发送配置信息")
                client_socket.close()
                return
            
            config_size = struct.unpack('!I', size_data)[0]
            
            # 接收配置信息
            config_data = self.recv_exact(client_socket, config_size)
            if not config_data:
                print(f"⚠️  {client_address} 配置信息不完整")
                client_socket.close()
                return
            
            config = json.loads(config_data.decode('utf-8'))
            
            client_socket.settimeout(None)
            
            # 判断客户端类型
            if 'fps' in config:
                # 发送端
                client_id = f"{client_address[0]}:{client_address[1]}"
                self.handle_sender(client_socket, client_address, client_id, config)
            else:
                # 接收端
                sender_id = config.get('sender_id', 'default')
                self.handle_receiver(client_socket, client_address, sender_id)
        
        except Exception as e:
            print(f"❌ 处理客户端失败 {client_address}: {e}")
            client_socket.close()
    
    def handle_sender(self, client_socket, client_address, client_id, config):
        """处理发送端"""
        print(f"📤 发送端: {client_address}")
        print(f"   ID: {client_id}")
        print(f"   区域: {config['region']}")
        print(f"   分辨率: {config['width']}x{config['height']}")
        print(f"   帧率: {config['fps']} FPS")
        
        # 使用 'default' 作为默认 ID，方便接收端连接
        sender_id = 'default'
        
        with self.sender_lock:
            self.senders[sender_id] = {
                'socket': client_socket,
                'address': client_address,
                'config': config,
                'stats': {'frames': 0, 'bytes': 0},
                'client_id': client_id
            }
        
        try:
            while self.running:
                # 接收帧大小
                size_data = self.recv_exact(client_socket, 4)
                if not size_data:
                    break
                
                frame_size = struct.unpack('!I', size_data)[0]
                
                # 接收帧数据
                frame_data = self.recv_exact(client_socket, frame_size)
                if not frame_data:
                    break
                
                # 更新统计
                sender_id = 'default'
                with self.sender_lock:
                    if sender_id in self.senders:
                        self.senders[sender_id]['stats']['frames'] += 1
                        self.senders[sender_id]['stats']['bytes'] += frame_size
                
                self.stats['total_frames'] += 1
                self.stats['total_bytes'] += frame_size
                
                # 转发给所有接收端
                self.broadcast_frame(sender_id, frame_data)
        
        except Exception as e:
            print(f"\n❌ 发送端断开 {client_address}: {e}")
        
        finally:
            sender_id = 'default'
            with self.sender_lock:
                if sender_id in self.senders:
                    del self.senders[sender_id]
            
            client_socket.close()
            print(f"🔌 发送端断开: {client_address}")
    
    def handle_receiver(self, client_socket, client_address, sender_id):
        """处理接收端"""
        print(f"📥 接收端: {client_address} (订阅: {sender_id})")
        
        with self.receiver_lock:
            if sender_id not in self.receivers:
                self.receivers[sender_id] = []
            self.receivers[sender_id].append(client_socket)
        
        try:
            # 保持连接
            while self.running:
                time.sleep(1)
        
        except Exception as e:
            print(f"\n❌ 接收端断开 {client_address}: {e}")
        
        finally:
            with self.receiver_lock:
                if sender_id in self.receivers:
                    if client_socket in self.receivers[sender_id]:
                        self.receivers[sender_id].remove(client_socket)
                    
                    if not self.receivers[sender_id]:
                        del self.receivers[sender_id]
            
            client_socket.close()
            print(f"🔌 接收端断开: {client_address}")
    
    def broadcast_frame(self, sender_id, frame_data):
        """广播帧数据给所有接收端"""
        with self.receiver_lock:
            if sender_id not in self.receivers:
                return
            
            frame_size = len(frame_data)
            size_data = struct.pack('!I', frame_size)
            
            dead_receivers = []
            
            for receiver_socket in self.receivers[sender_id]:
                try:
                    receiver_socket.sendall(size_data)
                    receiver_socket.sendall(frame_data)
                except:
                    dead_receivers.append(receiver_socket)
            
            # 移除断开的接收端
            for receiver_socket in dead_receivers:
                self.receivers[sender_id].remove(receiver_socket)
                try:
                    receiver_socket.close()
                except:
                    pass
    
    def recv_exact(self, sock, size):
        """接收指定大小的数据"""
        data = b''
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def print_stats_loop(self):
        """定期打印统计信息"""
        while self.running:
            time.sleep(5)
            self.print_stats()
    
    def print_stats(self):
        """打印统计信息"""
        if not self.stats['start_time']:
            return
        
        elapsed = time.time() - self.stats['start_time']
        
        print("\n" + "=" * 60)
        print("📊 服务器统计")
        print("=" * 60)
        
        with self.sender_lock:
            print(f"发送端数量: {len(self.senders)}")
            for sender_id, info in self.senders.items():
                stats = info['stats']
                print(f"  [{sender_id}] {info.get('client_id', 'N/A')}")
                print(f"    帧数: {stats['frames']}")
                print(f"    数据: {stats['bytes'] / 1024 / 1024:.2f} MB")
        
        with self.receiver_lock:
            total_receivers = sum(len(receivers) for receivers in self.receivers.values())
            print(f"接收端数量: {total_receivers}")
        
        print(f"\n总帧数: {self.stats['total_frames']}")
        print(f"总数据: {self.stats['total_bytes'] / 1024 / 1024:.2f} MB")
        
        if elapsed > 0:
            print(f"平均 FPS: {self.stats['total_frames'] / elapsed:.1f}")
            print(f"平均速率: {(self.stats['total_bytes'] * 8 / 1024 / 1024) / elapsed:.2f} Mbps")
        
        print("=" * 60)
    
    def stop(self):
        """停止服务器"""
        self.running = False
        
        # 关闭所有连接
        with self.sender_lock:
            for info in self.senders.values():
                try:
                    info['socket'].close()
                except:
                    pass
            self.senders.clear()
        
        with self.receiver_lock:
            for receivers in self.receivers.values():
                for receiver_socket in receivers:
                    try:
                        receiver_socket.close()
                    except:
                        pass
            self.receivers.clear()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("\n✅ 服务器已停止")


if __name__ == "__main__":
    import sys
    
    # 默认参数
    host = '0.0.0.0'
    port = 5003
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    server = ScreenServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  停止服务器")
        server.stop()
