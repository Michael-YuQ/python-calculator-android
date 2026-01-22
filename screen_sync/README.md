# 屏幕同步系统

实时同步屏幕右侧 1/4 区域到远程设备，支持每秒 4 帧传输。

## 系统架构

```
发送端 (Windows/Linux) --> 服务器 (CentOS) --> 接收端 (Windows/Linux)
```

## 功能特性

- 📺 捕获屏幕右侧 1/4 区域
- 🎬 可配置帧率（默认 4 FPS）
- 🗜️ JPEG 压缩传输
- 🔄 自动重连机制
- 📊 实时统计信息
- 🖥️ GUI 显示接收画面
- 🌐 支持多客户端

## 安装依赖

### Windows/Linux 客户端

```bash
pip install -r requirements.txt
```

### CentOS 服务器

```bash
# Python 3.6+
yum install python3 python3-pip

# 安装依赖（服务器端不需要 Pillow）
# 无需额外依赖
```

## 使用方法

### 1. 启动服务器（CentOS）

```bash
python3 server.py [端口]
```

示例：
```bash
# 使用默认端口 5003
python3 server.py

# 使用自定义端口
python3 server.py 8888
```

### 2. 启动发送端（Windows/Linux）

```bash
python client_sender.py [服务器IP] [端口] [帧率]
```

示例：
```bash
# 连接到本地服务器
python client_sender.py localhost 5003 4

# 连接到远程服务器
python client_sender.py 192.168.1.100 5003 4

# 使用更高帧率
python client_sender.py 192.168.1.100 5003 10
```

### 3. 启动接收端（Windows/Linux）

```bash
python client_receiver.py [服务器IP] [端口] [发送端ID]
```

示例：
```bash
# 连接到本地服务器
python client_receiver.py localhost 5003

# 连接到远程服务器
python client_receiver.py 192.168.1.100 5003
```

## 配置说明

### 修改捕获区域

编辑 `client_sender.py` 中的 `get_screen_region()` 方法：

```python
def get_screen_region(self):
    screen = ImageGrab.grab()
    width, height = screen.size
    
    # 右侧 1/4
    left = width * 3 // 4
    
    # 修改为其他区域，例如左侧 1/4：
    # left = 0
    # right = width // 4
    
    return (left, 0, width, height)
```

### 修改压缩质量

编辑 `client_sender.py` 中的 `capture_frame()` 方法：

```python
screenshot.save(buffer, format='JPEG', quality=75, optimize=True)
# quality: 1-100，越高质量越好但文件越大
```

## 防火墙配置

### CentOS 服务器

```bash
# 开放端口
firewall-cmd --permanent --add-port=5003/tcp
firewall-cmd --reload

# 或关闭防火墙（不推荐）
systemctl stop firewalld
```

## 性能优化

### 降低延迟
- 提高帧率（增加 CPU 和网络负载）
- 降低 JPEG 质量
- 使用有线网络

### 降低带宽
- 降低帧率
- 提高 JPEG 压缩率
- 减小捕获区域

## 故障排除

### 连接失败
1. 检查服务器是否启动
2. 检查防火墙设置
3. 检查 IP 地址和端口

### 画面卡顿
1. 降低帧率
2. 提高网络带宽
3. 降低图像质量

### 内存占用高
1. 降低帧率
2. 减小捕获区域

## 系统要求

- Python 3.6+
- Pillow (客户端)
- 网络带宽: 建议 1 Mbps+

## 许可证

MIT License
