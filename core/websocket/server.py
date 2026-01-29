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

    async def _send_state(self, websocket):
        """持续发送当前状态给前端"""
        while True:
            try:
                # 添加当前播放音乐信息
                state = self.current_command.copy()
                state['current_music'] = self.current_command.get('current_music', None)
                await websocket.send(json.dumps(state))
                await asyncio.sleep(0.2)  # 提高刷新率到0.2秒
            except websockets.exceptions.ConnectionClosed:
                break

    async def _receive_command(self, websocket):
        """接收前端发来的控制指令"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if "command" in data:
                        print(f"📡 收到前端指令: {data['command']}")
                        # 1. 设置指令
                        self.current_command['command'] = data['command']
                        self.current_command['confidence'] = 1.0

                        # 2. 维持一小段时间（脉冲），确保MusicPlayer能检测到
                        # 注意：这里会阻塞接收循环0.3秒，但对于简单的控制是可接受的
                        await asyncio.sleep(0.3)

                        # 3. 只有当指令未改变时才重置（防止覆盖了期间产生的新指令）
                        if self.current_command['command'] == data['command']:
                            self.current_command['command'] = 'idle'
                            self.current_command['confidence'] = 0.0

                except json.JSONDecodeError:
                    print("❌ 收到无效JSON数据")
        except websockets.exceptions.ConnectionClosed:
            pass

    async def handle_client(self, websocket):
        """处理前端客户端连接（双向通信）"""
        print(f"✅ 前端已连接：{websocket.remote_address}")

        # 并发执行发送状态和接收指令
        producer = asyncio.create_task(self._send_state(websocket))
        consumer = asyncio.create_task(self._receive_command(websocket))

        # 等待任意一个任务结束（通常是连接断开）
        done, pending = await asyncio.wait(
            [producer, consumer], 
            return_when=asyncio.FIRST_COMPLETED
        )

        # 清理未完成的任务
        for task in pending:
            task.cancel()

        print(f"❌ 前端断开连接：{websocket.remote_address}")

    async def start_server_async(self):
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # run forever

    def run(self):
        """启动WebSocket服务"""
        try:
            asyncio.run(self.start_server_async())
        except Exception as e:
            print(f"WebSocket Server Error: {e}")