#!/usr/bin/env python3
"""
WebSocket 服务器 - 向 SelfAgent App 推送消息
部署到服务器后运行: python ws_server.py
App 会自动连接 ws://111.170.6.103:9999/ws
"""

import asyncio
import websockets
import json
from datetime import datetime

# 存储所有连接的客户端
clients = set()

async def handler(websocket, path):
    """处理客户端连接"""
    clients.add(websocket)
    client_ip = websocket.remote_address[0]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 新连接: {client_ip} (在线: {len(clients)})")
    
    try:
        async for message in websocket:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到: {message}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 断开: {client_ip} (在线: {len(clients)})")

async def broadcast(message):
    """向所有客户端广播消息"""
    if clients:
        msg = json.dumps({"title": "服务器通知", "body": message, "time": datetime.now().strftime('%H:%M:%S')})
        await asyncio.gather(*[client.send(msg) for client in clients])
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 已推送给 {len(clients)} 个客户端")

async def input_loop():
    """命令行输入，输入消息后推送给所有客户端"""
    print("\n" + "="*50)
    print("WebSocket 服务器已启动 - ws://0.0.0.0:9999/ws")
    print("输入消息后回车即可推送到所有 App")
    print("="*50 + "\n")
    
    loop = asyncio.get_event_loop()
    while True:
        message = await loop.run_in_executor(None, input, "推送消息> ")
        if message.strip():
            await broadcast(message.strip())

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 9999, path="/ws")
    await asyncio.gather(server.wait_closed(), input_loop())

if __name__ == "__main__":
    asyncio.run(main())
