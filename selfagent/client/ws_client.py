#!/usr/bin/env python3
"""
WebSocket 客户端 - 接收服务器推送并弹出 Windows 通知
运行: python ws_client.py
"""

import asyncio
import websockets
import json
from datetime import datetime

# Windows 通知
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False
    print("提示: pip install win10toast 可启用 Windows 通知")

WS_URL = "ws://111.170.6.103:10002/ws"

def show_notification(title, body):
    """显示 Windows 通知"""
    print(f"\n🔔 [{datetime.now().strftime('%H:%M:%S')}] {title}: {body}")
    if HAS_TOAST:
        try:
            toaster.show_toast(title, body, duration=5, threaded=True)
        except:
            pass

async def connect():
    """连接 WebSocket 并监听消息"""
    while True:
        try:
            print(f"正在连接 {WS_URL} ...")
            async with websockets.connect(WS_URL) as ws:
                print("✅ 已连接，等待消息...\n")
                async for message in ws:
                    try:
                        data = json.loads(message)
                        title = data.get("title", "通知")
                        body = data.get("body", message)
                    except:
                        title, body = "通知", message
                    show_notification(title, body)
        except Exception as e:
            print(f"❌ 连接失败: {e}")
        print("5秒后重连...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    print("="*40)
    print("WebSocket 客户端 - 接收服务器推送")
    print("="*40)
    asyncio.run(connect())
