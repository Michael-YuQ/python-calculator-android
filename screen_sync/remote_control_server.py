"""
远程控制服务器端
用于向客户端发送控制命令
"""

import socket
import json
import struct
import sys


class RemoteControlServer:
    def __init__(self, host='0.0.0.0', command_port=5004):
        self.host = host
        self.command_port = command_port
        self.clients = []  # 连接的客户端列表
        self.server_socket = None
    
    def start(self):
        """启动命令服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.command_port))
            self.server_socket.listen(10)
            
            print("=" * 60)
            print("远程控制服务器 - 命令端口")
            print("=" * 60)
            print(f"✅ 监听端口: {self.command_port}")
            print("💡 等待客户端连接...\n")
            
            import threading
            
            # 启动接受连接线程
            accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            accept_thread.start()
            
            # 命令行界面
            self.command_interface()
        
        except Exception as e:
            print(f"❌ 启动失败: {e}")
    
    def accept_clients(self):
        """接受客户端连接"""
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append({
                    'socket': client_socket,
                    'address': client_address
                })
                print(f"\n✅ 客户端连接: {client_address}")
                print(f"   当前客户端数: {len(self.clients)}\n")
                print(">>> ", end='', flush=True)
            except:
                break
    
    def command_interface(self):
        """命令行界面"""
        print("=" * 60)
        print("命令列表:")
        print("=" * 60)
        print("  start          - 开启屏幕共享")
        print("  stop           - 停止屏幕共享")
        print("  input <文本>   - 在 Kiro 中输入文本")
        print("  clients        - 显示连接的客户端")
        print("  quit           - 退出")
        print("=" * 60)
        print()
        
        while True:
            try:
                cmd = input(">>> ").strip()
                
                if not cmd:
                    continue
                
                if cmd == 'quit':
                    break
                
                elif cmd == 'clients':
                    self.show_clients()
                
                elif cmd == 'start':
                    self.send_screen_control('start')
                
                elif cmd == 'stop':
                    self.send_screen_control('stop')
                
                elif cmd.startswith('input '):
                    text = cmd[6:].strip()
                    if text:
                        self.send_kiro_input(text)
                    else:
                        print("⚠️  请输入文本")
                
                else:
                    print(f"⚠️  未知命令: {cmd}")
            
            except KeyboardInterrupt:
                print("\n")
                break
            except EOFError:
                break
        
        self.stop()
    
    def show_clients(self):
        """显示连接的客户端"""
        if not self.clients:
            print("⚠️  没有连接的客户端")
            return
        
        print(f"\n连接的客户端 ({len(self.clients)}):")
        for i, client in enumerate(self.clients):
            print(f"  [{i}] {client['address']}")
        print()
    
    def send_screen_control(self, action):
        """发送屏幕控制命令"""
        command = {
            'type': 'screen_control',
            'action': action
        }
        
        self.broadcast_command(command)
        
        if action == 'start':
            print("✅ 已发送：开启屏幕共享")
        elif action == 'stop':
            print("⏸️  已发送：停止屏幕共享")
    
    def send_kiro_input(self, text):
        """发送 Kiro 输入命令"""
        command = {
            'type': 'kiro_input',
            'text': text
        }
        
        self.broadcast_command(command)
        print(f"✅ 已发送 Kiro 输入: {text}")
    
    def broadcast_command(self, command):
        """广播命令到所有客户端"""
        if not self.clients:
            print("⚠️  没有连接的客户端")
            return
        
        cmd_json = json.dumps(command).encode('utf-8')
        cmd_size = struct.pack('!I', len(cmd_json))
        
        dead_clients = []
        
        for client in self.clients:
            try:
                client['socket'].sendall(cmd_size)
                client['socket'].sendall(cmd_json)
            except:
                dead_clients.append(client)
        
        # 移除断开的客户端
        for client in dead_clients:
            self.clients.remove(client)
            print(f"⚠️  客户端断开: {client['address']}")
    
    def stop(self):
        """停止服务器"""
        for client in self.clients:
            try:
                client['socket'].close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("\n✅ 服务器已停止")


if __name__ == "__main__":
    # 默认参数
    host = '0.0.0.0'
    command_port = 5004
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command_port = int(sys.argv[1])
    
    server = RemoteControlServer(host, command_port)
    server.start()
