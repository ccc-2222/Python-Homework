
"""
WebSocket服务（负责：转发手势指令给前端）
"""
import asyncio
import websockets
import json

class WebSocketServer:
    def __init__(self, current_command):
        self.host = "127.0.0.1"
        self.port = 8765  # 固定端口，和前端一致
        self.current_command = current_command  # 关联全局手势指令

    async def handle_client(self, websocket):
        """处理前端客户端连接"""
        print(f"✅ 前端已连接：{websocket.remote_address}")
        try:
            while True:
                # 每秒向前端发送1次当前手势指令
                await websocket.send(json.dumps(self.current_command))
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            print(f"❌ 前端断开连接：{websocket.remote_address}")

    def run(self):
        """启动WebSocket服务"""
        start_server = websockets.serve(self.handle_client, self.host, self.port)
        asyncio.run(start_server)