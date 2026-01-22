"""
测试服务器连接
"""

import socket
import sys


def test_connection(host, port):
    """测试连接到服务器"""
    
    print("=" * 60)
    print("服务器连接测试")
    print("=" * 60)
    print(f"目标: {host}:{port}")
    print()
    
    # 测试1: DNS 解析
    print("[1/3] DNS 解析测试...")
    try:
        import socket
        ip = socket.gethostbyname(host)
        print(f"✅ DNS 解析成功: {host} -> {ip}")
    except Exception as e:
        print(f"❌ DNS 解析失败: {e}")
        return False
    
    # 测试2: Ping 测试
    print("\n[2/3] Ping 测试...")
    try:
        import subprocess
        import platform
        
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(f"✅ Ping 成功")
        else:
            print(f"⚠️  Ping 失败（可能服务器禁用了 ICMP）")
    except Exception as e:
        print(f"⚠️  Ping 测试失败: {e}")
    
    # 测试3: TCP 连接
    print(f"\n[3/3] TCP 连接测试 (端口 {port})...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"✅ TCP 连接成功！端口 {port} 已开放")
            sock.close()
            return True
        else:
            print(f"❌ TCP 连接失败")
            print(f"   错误码: {result}")
            print(f"\n可能的原因:")
            print(f"   1. 服务器未启动")
            print(f"   2. 防火墙阻止了端口 {port}")
            print(f"   3. 端口号不正确")
            print(f"   4. 网络不通")
            sock.close()
            return False
    
    except socket.timeout:
        print(f"❌ 连接超时")
        print(f"   服务器可能未响应或网络延迟过高")
        return False
    
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def test_server_response(host, port):
    """测试服务器响应"""
    
    print("\n" + "=" * 60)
    print("服务器响应测试")
    print("=" * 60)
    
    try:
        import json
        import struct
        
        print(f"连接到 {host}:{port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        print("✅ 已连接")
        
        # 发送接收端配置
        print("发送配置信息...")
        config = {'sender_id': 'test'}
        config_json = json.dumps(config).encode('utf-8')
        
        sock.sendall(struct.pack('!I', len(config_json)))
        sock.sendall(config_json)
        
        print("✅ 配置已发送")
        print("⏳ 等待数据...")
        
        # 尝试接收数据
        sock.settimeout(5)
        data = sock.recv(4)
        
        if data:
            print(f"✅ 收到数据: {len(data)} 字节")
            print("   服务器正在工作！")
        else:
            print("⚠️  未收到数据")
            print("   可能没有发送端在线")
        
        sock.close()
        return True
    
    except socket.timeout:
        print("⚠️  等待超时")
        print("   服务器已连接但没有数据")
        print("   可能原因：没有发送端在线")
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    host = '111.170.6.103'
    port = 5003
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # 基础连接测试
    if test_connection(host, port):
        print("\n✅ 基础连接测试通过")
        
        # 服务器响应测试
        test_server_response(host, port)
    else:
        print("\n❌ 基础连接测试失败")
        print("\n💡 解决建议:")
        print("   1. 确认服务器已启动: ssh 到服务器运行 'python3 server.py'")
        print("   2. 检查防火墙: firewall-cmd --list-ports")
        print("   3. 开放端口: firewall-cmd --permanent --add-port=5003/tcp")
        print("   4. 检查服务器监听: netstat -tlnp | grep 5003")
    
    print("\n" + "=" * 60)
